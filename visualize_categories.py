import sqlite3
import matplotlib.pyplot as plt

# Connect to SQLite database
conn = sqlite3.connect("project_data.db")
cur = conn.cursor()

# --- BAR CHART: Top 10 Business Categories ---
cur.execute("""
    SELECT category, COUNT(*) as count FROM businesses
    WHERE category IS NOT NULL
    GROUP BY category
    ORDER BY count DESC
    LIMIT 10
""")
results = cur.fetchall()

categories = [row[0] for row in results]
counts = [row[1] for row in results]

# Reverse to plot with highest at top
categories.reverse()
counts.reverse()

# Custom colors: Highlight the most common one
colors = ['#4B8BBE'] * len(categories)
colors[-1] = '#306998'  # Highlight top category

# Plot bar chart
plt.figure(figsize=(10, 6))
plt.barh(categories, counts, color=colors)
plt.xlabel("Number of Businesses")
plt.title("Top 10 Business Categories (Foursquare Data)")

# Add labels
for i, v in enumerate(counts):
    plt.text(v + 0.1, i, str(v), va='center')

plt.show()
