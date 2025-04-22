import requests
import sqlite3
import os
import random
from dotenv import load_dotenv
import matplotlib.pyplot as plt

# Load API key from .env
load_dotenv()
API_KEY = os.getenv("FOURSQUARE_API_KEY")


def create_database():
    """
    Creates a SQLite database and initializes the 'businesses' table if it doesn't exist.
    Input: None
    Output: Returns a connection and cursor object for the database.
    """
    conn = sqlite3.connect("project_data.db")
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS businesses (
            bus_id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
            fsq_id TEXT UNIQUE,
            name TEXT,
            category INTEGER,
            address TEXT,
            latitude REAL,
            longitude REAL,
            rating REAL
        )
    """)
    conn.commit()
    cur.execute(
        "CREATE TABLE IF NOT EXISTS categories (id INTEGER PRIMARY KEY AUTOINCREMENT, category TEXT UNIQUE)"
    )
    return conn, cur


def fetch_and_store_business_data(cur, conn):
    """
    Fetches restaurant data from the Foursquare API and stores up to 25 unique businesses
    into the local SQLite database.

    Input:
    - cur: SQLite cursor object
    - conn: SQLite connection object

    Output: None (data is stored directly in the database)
    """
    headers = {
        "Accept": "application/json",
        "Authorization": API_KEY
    }
    ##randomizes location for better graphs 
    totalsize = cur.execute("""SELECT COUNT(*) FROM businesses""").fetchone()[0]/1000
    lat = 42.2808 + random.uniform(totalsize*-1, totalsize)
    long = -83.7430 + random.uniform(totalsize*-1, totalsize)

    params = {
        "ll": f"{lat},{long}",
        "query": "restaurant",
        "limit": 50
    }

    response = requests.get("https://api.foursquare.com/v3/places/search", headers=headers, params=params)
    data = response.json()
    cat_id = 0
    inserted = 0
    for place in data.get("results", []):
        if inserted >= 25:
            break

        fsq_id = place['fsq_id']
        cur.execute("SELECT 1 FROM businesses WHERE fsq_id = ?", (fsq_id,))
        if cur.fetchone():
            continue

        # Fetch additional details like rating
        detail_url = f"https://api.foursquare.com/v3/places/{fsq_id}"
        detail_res = requests.get(detail_url, headers=headers)
        detail_data = detail_res.json()
        rating = detail_data.get('rating')
        tempcat = place['categories'][0]['name'] if place.get('categories') else None
        result = cur.execute("""
            SELECT id FROM categories WHERE category = ?
        """, (tempcat,)).fetchone()
        if result: 
            cat_id = result[0]
        else: 
            cur.execute("""
            INSERT INTO categories (category) VALUES (?)
         """, (tempcat,))
            cat_id = cur.lastrowid


        cur.execute("""
            INSERT OR IGNORE INTO businesses (fsq_id, name, category, address, latitude, longitude, rating)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            fsq_id,
            place['name'],
            cat_id,
            place['location'].get('formatted_address'),
            place['geocodes']['main']['latitude'],
            place['geocodes']['main']['longitude'],
            rating
        ))
        inserted += 1

    conn.commit()
    print("✅ Data saved to project_data.db")


if __name__ == "__main__":
    conn, cur = create_database()
    fetch_and_store_business_data(cur, conn)
    
    conn.close()

