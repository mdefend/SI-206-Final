import sqlite3
import json
import os 
import requests
import seaborn as sb 
import matplotlib.pyplot as plt
from dotenv import load_dotenv

API_KEY = os.getenv("WEATHER_API_KEY")
#weather time! 
def weatherdatabasesetup(cur,conn):
    #To Do: setup weather table 
    cur.execute("CREATE TABLE IF NOT EXISTS weather(location INTEGER PRIMARY KEY UNIQUE, avg_temp INTEGER, avg_condition string)")
    
def weatherapicall(location,cur,conn):
    #To Do: collect api calls and add to table: 
    for row in location:
        lat = row[1] 
        long = row[2] 
        url =  "http://api.weatherapi.com/v1/forecast.json?key=" + API_KEY + "&q=" + str(lat) + "," + str(long) + "&days=7"
        response = requests.get(url)
        if response.status_code == 200: 
            data = response.json()
            days = data.get("forecast", {}).get("forecastday", [])
            av_temp = sum(day["day"]["avgtemp_f"] for day in days) / len(days)
            av_condition =  sum(day["day"].get("daily_will_it_rain", 0) for day in days) / len(days) 
            cur.execute("""
                    INSERT OR IGNORE INTO weather (location, avg_temp, avg_condition)
                    VALUES (?, ?, ?)
                """, (row[0], av_temp, av_condition)) 
           
             


     



def visuals(): 
    query = """
        SELECT b.category AS restaurant_type, w.avg_temp AS avg_temp,
        COUNT(*) AS count
        FROM businesses b
        JOIN weather w ON b.bus_id = w.location
        GROUP BY b.category
        ORDER BY count DESC
        LIMIT 10;
        """
    conn = sqlite3.connect("project_data.db")
    cur = conn.cursor() 
    results = cur.execute(query).fetchall()
    types = [row[0] for row in results]
    avg_temp = [row[1] for row in results]
    count = [row[2] for row in results]
    conn.close()
    plt.figure(figsize=(10, 6))
    sb.scatterplot(x=count , y=avg_temp, hue=types, palette='icefire')
    plt.title("Average Temperature vs Number of Restaurants By Type")
    plt.xlabel("Count")
    plt.ylabel("Average Temperature (f)")
    plt.legend(title='Restaurant Type', bbox_to_anchor=(1.02, 1), loc='upper left')

    plt.tight_layout()
    plt.show()



    
def main ():
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path + "/" + "project_data.db")
    cur = conn.cursor() 
    weatherdatabasesetup(cur,conn)
    cur.execute("SELECT COUNT(*) FROM businesses")
    businesses_count = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM weather")
    weather_count = cur.fetchone()[0]
    ## get locations from foursquare table
    if weather_count != businesses_count: 
        results = cur.execute("SELECT bus_id, latitude, longitude FROM businesses LIMIT ? OFFSET ?",(25,weather_count)).fetchall()
        weatherapicall(results, cur, conn)
        conn.commit()
    else: 
        visuals()


           
    ## then call the weather api to get the dates needed for this: 
if __name__ == "__main__":
    main()