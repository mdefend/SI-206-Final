import sqlite3
import matplotlib.pyplot as plt

conn = sqlite3.connect("project_data.db")
cur = conn.cursor()

cur.execute("""
    SELECT price, COUNT(*) FROM businesses
    WHERE price IS NOT NULL
    GROUP BY price
    ORDER BY price
""")
price_data = cur.fetchall()
conn.close()

price_labels = [f"${'$'*row[0]}" for row in price_data]
price_counts = [row[1] for row in price_data]

plt.figure(figsize=(6, 6))
plt.pie(price_counts, labels=price_labels, autopct='%1.1f%%', startangle=140)
plt.title("Business Price Tier Distribution")
plt.tight_layout()
plt.show()
