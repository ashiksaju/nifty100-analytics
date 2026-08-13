import sqlite3

DB_PATH = r"C:\Users\ashik\OneDrive\Desktop\nifty100-analytics\data\database\nifty100.db"

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

print("=" * 60)
print("NIFTY100 DOCUMENTS DATABASE CHECK")
print("=" * 60)

print("\nDOCUMENTS TABLE COLUMNS")
print("-" * 60)

columns = cursor.execute(
    "PRAGMA table_info(documents)"
).fetchall()

for column in columns:
    print(column)

print("\nDOCUMENT ROW COUNT")
print("-" * 60)

count = cursor.execute(
    "SELECT COUNT(*) FROM documents"
).fetchone()[0]

print("Rows:", count)

print("\nSAMPLE DOCUMENT DATA")
print("-" * 60)

rows = cursor.execute(
    "SELECT * FROM documents LIMIT 10"
).fetchall()

for row in rows:
    print(row)

print("\nDOCUMENTS FOR ABB")
print("-" * 60)

abb_rows = cursor.execute(
    """
    SELECT *
    FROM documents
    WHERE UPPER(company_id) = 'ABB'
    """
).fetchall()

for row in abb_rows:
    print(row)

print("\nABB DOCUMENT COUNT:", len(abb_rows))

print("\n" + "=" * 60)
print("DATABASE CHECK COMPLETE")
print("=" * 60)

conn.close()