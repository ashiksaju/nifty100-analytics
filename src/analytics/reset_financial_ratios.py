import sqlite3

DATABASE = "data/database/nifty100.db"

conn = sqlite3.connect(DATABASE)
cursor = conn.cursor()

cursor.execute("DROP TABLE IF EXISTS financial_ratios")

conn.commit()
conn.close()

print("financial_ratios table dropped successfully.")