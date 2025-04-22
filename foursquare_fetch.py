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
            category TEXT,
            address TEXT,
            latitude REAL,
            longitude REAL,
            rating REAL
        )
    """)
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

    lat = 42.2808 + random.uniform(-0.01, 0.01)
    long = -83.7430 + random.uniform(-0.01, 0.01)

    params = {
        "ll": f"{lat},{long}",
        "query": "restaurant",
        "limit": 50
    }

    response = requests.get("https://api.foursquare.com/v3/places/search", headers=headers, params=params)
    data = response.json()

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
    print("✅ Data saved to project_data.db")


def display_and_plot_category_counts(cur):
    """
    Queries the top 10 business categories by count from the database,
    prints them to the terminal, and generates a horizontal bar chart.

    Input:
    - cur: SQLite cursor object

    Output: A matplotlib bar chart is displayed and category counts are printed to terminal.
    """
    cur.execute("""
        SELECT category, COUNT(*) as count FROM businesses
        WHERE category IS NOT NULL
        GROUP BY category
        ORDER BY count DESC
        LIMIT 10
    """)
    results = cur.fetchall()

    print("Top 10 Business Categories and Counts:")
    for category, count in results:
        print(f"{category}: {count}")

    categories = [row[0] for row in results]
    counts = [row[1] for row in results]

    categories.reverse()
    counts.reverse()

    colors = ['#4B8BBE'] * len(categories)
    colors[-1] = '#306998'

    plt.figure(figsize=(10, 6))
    plt.barh(categories, counts, color=colors)
    plt.xlabel("Number of Businesses")
    plt.title("Top 10 Business Categories (Foursquare Data)")

    for i, v in enumerate(counts):
        plt.text(v + 0.1, i, str(v), va='center')

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    conn, cur = create_database()
    fetch_and_store_business_data(cur, conn)
    display_and_plot_category_counts(cur)
    conn.close()

