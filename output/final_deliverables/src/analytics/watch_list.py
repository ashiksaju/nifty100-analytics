from pathlib import Path
import sqlite3

import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[2]

DATABASE = BASE_DIR / "data" / "database" / "nifty100.db"

def load_percentiles():

    conn = sqlite3.connect(DATABASE)

    df = pd.read_sql(
        "SELECT * FROM peer_percentiles",
        conn,
    )

    conn.close()

    return df

def detect_watch_list(df):

    bottom = df[
        df["percentile_rank"] <= 25
    ]

    summary = (
        bottom.groupby("company_id")
        .size()
        .reset_index(name="bottom_metrics")
    )

    summary["flag"] = summary[
        "bottom_metrics"
    ].apply(
        lambda x:
        "Watch List"
        if x >= 4
        else ""
    )

    summary = summary[
        summary["flag"] != ""
    ]

    return summary

def save_table(df):

    conn = sqlite3.connect(DATABASE)

    df.to_sql(
        "watch_list",
        conn,
        if_exists="replace",
        index=False,
    )

    conn.close()

def main():

    df = load_percentiles()

    result = detect_watch_list(df)

    save_table(result)

    print()

    print(result.head())

    print()

    print("Companies :", len(result))


if __name__ == "__main__":
    main()