from pathlib import Path
import sqlite3

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

def latest_records(df):

    df = df.copy()

    df["year_num"] = (
        df["year"]
        .astype(str)
        .str.extract(r"(\d{4})")
        .astype(float)
    )

    latest = (
        df
        .sort_values(
            ["company_id", "year_num"]
        )
        .groupby("company_id")
        .tail(1)
    )

    return latest.drop(columns="year_num")

def merge_peer_groups(
    financial,
    peer,
):

    latest = latest_records(
        financial,
    )

    merged = latest.merge(
        peer,
        on="company_id",
        how="left",
    )

    return merged

COMPARE_COLUMNS = [

    "company_id",

    "company_name",

    "peer_group_name",

    "roe_percentage",

    "roce_percentage",

    "net_profit_margin_pct",

    "operating_profit_margin_pct",

    "return_on_assets_pct",

    "return_on_equity_pct",

    "return_on_capital_employed_pct",

    "debt_to_equity",

    "interest_coverage",

    "asset_turnover",

    "free_cash_flow_cr",

    "cfo_quality_score",

    "fcf_conversion_rate",

    "revenue_cagr_5yr",

    "pat_cagr_5yr",

    "eps_cagr_5yr",

    "capex_label",

    "composite_quality_score",
]

def build_table(df):

    table = df[
        COMPARE_COLUMNS
    ].copy()

    return table

def save_table(df):

    conn = sqlite3.connect(DATABASE)

    df.to_sql(

        "comparison_table",

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

    table = build_table(
        merged,
    )

    save_table(
        table,
    )

    print()

    print(table.head())

    print()

    print("Rows :", len(table))

    print("Columns :", len(table.columns))


if __name__ == "__main__":

    main()