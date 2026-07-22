from pathlib import Path
import sqlite3

import numpy as np
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[2]

DATABASE = BASE_DIR / "data" / "database" / "nifty100.db"

def load_tables():

    conn = sqlite3.connect(DATABASE)

    financial = pd.read_sql(
        "SELECT * FROM financial_ratios",
        conn,
    )

    peer = pd.read_sql(
        "SELECT * FROM peer_groups",
        conn,
    )

    conn.close()

    return financial, peer

METRICS = [
    "roe_percentage",
    "roce_percentage",
    "net_profit_margin_pct",
    "debt_to_equity",
    "cfo_quality_score",
    "pat_cagr_5yr",
    "revenue_cagr_5yr",
    "eps_cagr_5yr",
    "composite_quality_score",
    "asset_turnover",
]


def latest_records(df):

    df = df.copy()

    df["year_num"] = (
        df["year"]
        .astype(str)
        .str.extract(r"(\d{4})")
        .astype(float)
    )

    df = (
        df
        .sort_values(
            ["company_id", "year_num"]
        )
        .groupby("company_id")
        .tail(1)
    )

    return df.drop(columns="year_num")

def merge_peer_groups(financial, peer):

    latest = latest_records(financial)

    merged = latest.merge(
        peer,
        on="company_id",
        how="left",
    )

    return merged

def benchmark_companies(df):

    benchmark = df[
        df["is_benchmark"] == 1
    ].copy()

    return benchmark

def calculate_gap(df, benchmark):

    rows = []

    for _, company in df.iterrows():

        peer = company["peer_group_name"]

        if pd.isna(peer):
            continue

        bench = benchmark[
            benchmark["peer_group_name"] == peer
        ]

        if bench.empty:
            continue

        bench = bench.iloc[0]

        for metric in METRICS:

            company_value = pd.to_numeric(
                company[metric],
                errors="coerce",
            )

            benchmark_value = pd.to_numeric(
                bench[metric],
                errors="coerce",
            )

            if pd.isna(company_value) or pd.isna(benchmark_value):
                continue

            absolute_gap = company_value - benchmark_value

            if benchmark_value == 0:

                percentage_gap = np.nan

            else:

                percentage_gap = (
                    absolute_gap
                    / benchmark_value
                ) * 100

            rows.append(
                {
                    "company_id": company["company_id"],
                    "peer_group_name": peer,
                    "metric": metric,
                    "company_value": company_value,
                    "benchmark_company": bench["company_id"],
                    "benchmark_value": benchmark_value,
                    "absolute_gap": round(
                        absolute_gap,
                        2,
                    ),
                    "percentage_gap": round(
                        percentage_gap,
                        2,
                    ),
                    "year": company["year"],
                }
            )

    return pd.DataFrame(rows)

def save_table(result):

    conn = sqlite3.connect(DATABASE)

    result.to_sql(
        "benchmark_gap",
        conn,
        if_exists="replace",
        index=False,
    )

    conn.close()


def main():

    financial, peer = load_tables()

    merged = merge_peer_groups(
        financial,
        peer,
    )

    benchmark = benchmark_companies(
        merged,
    )

    result = calculate_gap(
        merged,
        benchmark,
    )

    save_table(
        result,
    )

    print()

    print(result.head())

    print()

    print("Rows :", len(result))


if __name__ == "__main__":
    main()