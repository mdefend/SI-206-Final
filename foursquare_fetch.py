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
        price INTEGER
    )
""")

# Insert data
for place in data.get("results", []):
    cur.execute("""
        INSERT OR IGNORE INTO businesses VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        place['fsq_id'],
        place['name'],
        place['categories'][0]['name'] if place.get('categories') else None,
        place['location'].get('formatted_address'),
        place['geocodes']['main']['latitude'],
        place['geocodes']['main']['longitude'],
        place.get('price')
    ))

conn.commit()
conn.close()

print("✅ Data saved to project_data.db")
