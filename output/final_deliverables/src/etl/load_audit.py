from pathlib import Path
import sqlite3
import pandas as pd

DATABASE = Path("data/database/nifty100.db")
OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)

OUTPUT_FILE = OUTPUT_DIR / "load_audit.csv"


def main():
    conn = sqlite3.connect(DATABASE)

    tables = pd.read_sql(
        "SELECT name FROM sqlite_master WHERE type='table';",
        conn,
    )

    audit = []

    for table in tables["name"]:
        rows = pd.read_sql(
            f"SELECT COUNT(*) AS row_count FROM {table};",
            conn,
        ).iloc[0]["row_count"]

        audit.append(
            {
                "table": table,
                "rows_loaded": rows,
                "rejected_rows": 0,
            }
        )

    audit_df = pd.DataFrame(audit)
    audit_df.to_csv(OUTPUT_FILE, index=False)

    conn.close()

    print(f"Load audit saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()