import requests
import sqlite3
import os
from dotenv import load_dotenv

# Load API key from .env
load_dotenv()
API_KEY = os.getenv("FOURSQUARE_API_KEY")

headers = {
    "Accept": "application/json",
    "Authorization": API_KEY
}

params = {
    "ll": "42.2808,-83.7430",  # Ann Arbor coords
    "query": "restaurant",
    "limit": 50
}

# Make API request
response = requests.get("https://api.foursquare.com/v3/places/search", headers=headers, params=params)
data = response.json()

# Create or connect to SQLite database
conn = sqlite3.connect("project_data.db")
cur = conn.cursor()

# Create table
cur.execute("""
    CREATE TABLE IF NOT EXISTS businesses (
        fsq_id TEXT PRIMARY KEY,
        name TEXT,
        category TEXT,
        address TEXT,
        latitude REAL,
        longitude REAL,
        rating REAL
    )
""")

# Insert data
for place in data.get("results", []):
    fsq_id = place['fsq_id']
    
    # Request additional details using Place Details API
    detail_url = f"https://api.foursquare.com/v3/places/{fsq_id}"
    detail_res = requests.get(detail_url, headers=headers)
    detail_data = detail_res.json()
    
    rating= detail_data.get('rating')  # Usually an integer from 1 to 4
    
    # Insert into DB
    cur.execute("""
        INSERT OR IGNORE INTO businesses VALUES (?, ?, ?, ?, ?, ?, ?)
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
