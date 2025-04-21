import sqlite3
import json
import os 
import requests
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
    
             


     
    
    
def main ():
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path + "/" + "project_data.db")
    cur = conn.cursor() 
    weatherdatabasesetup(cur,conn)
    ## get locations from foursquare table
    results = cur.execute("SELECT bus_id, latitude, longitude FROM businesses")
    
    while True: 
        section = results.fetchmany(size = 25)
        if not section: 
            break
        weatherapicall(section,cur,conn)

    conn.commit()


           
    ## then call the weather api to get the dates needed for this: 
if __name__ == "__main__":
    main()