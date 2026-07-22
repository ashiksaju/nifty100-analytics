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

def detect_best(df):

    top = df[
        df["percentile_rank"] >= 75
    ]

    summary = (
        top.groupby("company_id")
        .size()
        .reset_index(name="top_metrics")
    )

    summary["badge"] = summary[
        "top_metrics"
    ].apply(
        lambda x:
        "Best in Class"
        if x >= 6
        else ""
    )

    summary = summary[
        summary["badge"] != ""
    ]

    return summary

def save_table(df):

    conn = sqlite3.connect(DATABASE)

    df.to_sql(
        "best_in_class",
        conn,
        if_exists="replace",
        index=False,
    )

    conn.close()

def main():

    df = load_percentiles()

    result = detect_best(df)

    save_table(result)

    print()

    print(result.head())

    print()

    print("Companies :", len(result))


if __name__ == "__main__":
    main()