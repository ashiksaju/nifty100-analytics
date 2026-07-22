from pathlib import Path
import sqlite3

from src.etl.loader import load_all_data


DATABASE_DIR = Path("data/database")
DATABASE_DIR.mkdir(parents=True, exist_ok=True)

DATABASE_PATH = DATABASE_DIR / "nifty100.db"


def main():
    datasets = load_all_data()

    conn = sqlite3.connect(DATABASE_PATH)

    for table_name, df in datasets.items():

     if table_name == "financial_ratios":
        print(df.columns)

        df.to_sql(
            table_name,
            conn,
            if_exists="replace",
            index=False,
        )
        print(f"{table_name} loaded ({len(df)} rows)")

    conn.commit()
    conn.close()

    print(f"\nDatabase created successfully:")
    print(DATABASE_PATH)


if __name__ == "__main__":
    print("SQLite loader started...")
    main()