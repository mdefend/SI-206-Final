import sqlite3
import json
import os 
#weather time! 
def getweatherapikey(filename):
    file = open(filename,'r',encoding="utf-8")
    api_key_weather = file.readline().rstrip()
    file.close() 
    return api_key_weather
def weathertablesetup(db_name):
    #To Do: setup weather table 
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path + "/" + db_name)
    cur = conn.cursor()
    return cur, conn
    
def weatherapicall(api_key, location, dates):
    #To Do: collect api calls and add to table:

    pass 