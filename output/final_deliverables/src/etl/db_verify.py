from pathlib import Path
import sqlite3
import pandas as pd

DATABASE = Path("data/database/nifty100.db")


def main():
    conn = sqlite3.connect(DATABASE)

    tables = pd.read_sql(
        "SELECT name FROM sqlite_master WHERE type='table';",
        conn
    )

    print("\nTables in Database\n")
    print(tables)

    print("\nRow Counts\n")

    for table in tables["name"]:
        count = pd.read_sql(
            f"SELECT COUNT(*) AS rows FROM {table};",
            conn
        )
        print(f"{table:<20} {count.iloc[0,0]}")
    
    print("\nForeign Key Check\n")

    fk_check = pd.read_sql(
       "PRAGMA foreign_key_check;",
        conn
             )

    if fk_check.empty:
           print("No foreign key violations found.")
    else:
           print(fk_check)
    
    conn.close()

if __name__ == "__main__":
    main()