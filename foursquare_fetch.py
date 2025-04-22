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

MAX_INSERT_PER_RUN = 25
inserted = 0

# Base location
lat = 42.2808 + random.uniform(-0.01, 0.01)
long = -83.7430 + random.uniform(-0.01, 0.01)

params = {
    "ll": f"{lat},{long}",
    "query": "restaurant",
    "limit": 50  # Request more to filter out duplicates
}

response = requests.get("https://api.foursquare.com/v3/places/search", headers=headers, params=params)
data = response.json()

for place in data.get("results", []):
    if inserted >= MAX_INSERT_PER_RUN:
        break

    fsq_id = place['fsq_id']
    cur.execute("SELECT 1 FROM businesses WHERE fsq_id = ?", (fsq_id,))
    if cur.fetchone():
        continue

    # Get extra details like rating
    detail_url = f"https://api.foursquare.com/v3/places/{fsq_id}"
    detail_res = requests.get(detail_url, headers=headers)
    detail_data = detail_res.json()
    rating = detail_data.get('rating')

    cur.execute("""
        INSERT OR IGNORE INTO businesses (fsq_id, name, category, address, latitude, longitude, rating)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        fsq_id,
        place['name'],
        place['categories'][0]['name'] if place.get('categories') else None,
        place['location'].get('formatted_address'),
        place['geocodes']['main']['latitude'],
        place['geocodes']['main']['longitude'],
        rating
    ))
    inserted += 1


conn.commit()
conn.close()

print("✅ Data saved to project_data.db")
