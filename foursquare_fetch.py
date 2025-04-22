import requests
import sqlite3
import os
import random
from dotenv import load_dotenv

# Load API key from .env
load_dotenv()
API_KEY = os.getenv("FOURSQUARE_API_KEY")

# Create or connect to SQLite database
conn = sqlite3.connect("project_data.db")
cur = conn.cursor()

# Create table
cur.execute("""
    CREATE TABLE IF NOT EXISTS businesses (
        bus_id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
        fsq_id TEXT UNIQUE,
        name TEXT,
        category TEXT,
        address TEXT,
        latitude REAL,
        longitude REAL,
        rating REAL
    )
""")
headers = {
    "Accept": "application/json",
    "Authorization": API_KEY
}


  # shifting for larger range in data
lat = 42.2808
long = -83.7430

lat = lat + random.uniform(-0.5, 0.5)
long = long + random.uniform(-0.5, 0.5)

params = {
        "ll": f"{lat},{long}",
        "query": "restaurant",
        "limit": 25,
    }

# Make API request
response = requests.get("https://api.foursquare.com/v3/places/search", headers=headers, params=params)
data = response.json()


# Insert data
for place in data.get("results", []):

    fsq_id = place['fsq_id']
    cur.execute("SELECT 1 FROM businesses WHERE fsq_id = ?", (fsq_id,))
    exists = cur.fetchone()
    if not exists: 

    
        # Request additional details using Place Details API
        detail_url = f"https://api.foursquare.com/v3/places/{fsq_id}"
        detail_res = requests.get(detail_url, headers=headers)
        detail_data = detail_res.json()
        
        rating= detail_data.get('rating')  # Usually an integer from 1 to 4
        
        # Insert into DB
        cur.execute("""
            INSERT OR IGNORE INTO businesses (fsq_id, name, category, address, latitude, longitude, rating) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            fsq_id,
            place['name'],
            place['categories'][0]['name'] if place.get('categories') else None,
            place['location'].get('formatted_address'),
            place['geocodes']['main']['latitude'],
            place['geocodes']['main']['longitude'],
            rating  # ← now it won't be null if Foursquare provides it
            ))
        

conn.commit()
conn.close()

print("✅ Data saved to project_data.db")
