import sqlite3
import json
import os 
import seaborn as sb 
import matplotlib.pyplot as plt 

##what it does: 
## does the select and counts for the weather 
##then writes the results to a json file and ouputs a scatter plot 

def weatherscatter(cur): 
    query = """
        SELECT c.category AS restaurant_type, w.avg_temp AS avg_temp,
        COUNT(*) AS count
        FROM businesses b
        JOIN categories c ON b.category = c.id
        JOIN weather w ON b.bus_id = w.location
        GROUP BY c.category
        ORDER BY count DESC
        LIMIT 15;
        """
    results = cur.execute(query).fetchall()
    types = [row[0] for row in results]
    avg_temp = [row[1] for row in results]
    count = [row[2] for row in results]
    ##
    calculations = [
    {
        "business_type": types[i],
        "average_temperature": avg_temp[i],
        "count": count[i]
    }
    for i in range(len(types))
    ]
    with open("weather_calculations.json", "w") as f:
        json.dump(calculations,f,indent=4)

   
    plt.figure(figsize=(10, 6))
    sb.scatterplot(x=count , y=avg_temp, hue=types, palette='rocket')
    plt.title("Average Temperature vs Number of Businesses By Type")
    plt.xlabel("Count")
    plt.ylabel("Average Temperature (F)")
    plt.legend(title='Business Type', bbox_to_anchor=(1.02, 1), loc='upper left')
    plt.tight_layout()
    plt.show()
def display_and_plot_category_counts(cur):
    """
    Queries the top 10 business categories by count from the database,
    prints them to the terminal, and generates a horizontal bar chart.

    Input:
    - cur: SQLite cursor object

    Output: A matplotlib bar chart is displayed and category counts are printed to terminal.
    """
    cur.execute("""
        SELECT c.category AS category, COUNT(*) as count
        FROM businesses b
        JOIN categories c ON b.category = c.id
        GROUP BY c.category
        ORDER BY count DESC
        LIMIT 10
    """)
    results = cur.fetchall()


    categories = [row[0] for row in results]
    counts = [row[1] for row in results]

    categories.reverse()
    counts.reverse()
    counts_calc = [
        {"category": categories[i], "count": counts[i]}
        for i in range(len(categories))
    ]
    with open("calculations.json", "w") as f:
        json.dump(counts_calc, f, indent=4)
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
    conn = sqlite3.connect("project_data.db")
    cur = conn.cursor() 
    weatherscatter(cur)
    display_and_plot_category_counts(cur)