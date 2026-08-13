import pandas as pd
import sqlite3
import yaml
from pathlib import Path
from src.screener.presets import (
    QUALITY_COMPOUNDER,
    VALUE_PICK,
    GROWTH_ACCELERATOR,
    DIVIDEND_CHAMPION,
    DEBT_FREE_BLUECHIP,
    TURNAROUND_WATCH,
)

BASE_DIR = Path(__file__).resolve().parents[2]

DATABASE = BASE_DIR / "data" / "database" / "nifty100.db"
CONFIG = BASE_DIR / "src" / "config" / "screener_config.yaml"
def load_config():

    with open(CONFIG, "r") as file:
        config = yaml.safe_load(file)

    return config
def load_financial_ratios():
    
    print(DATABASE)

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("""
    SELECT name
    FROM sqlite_master
    WHERE type='table';
    """)

    print(cursor.fetchall())

    df = pd.read_sql(
        "SELECT * FROM financial_ratios",
        conn,
    )

    conn.close()
    numeric_columns = [
    "revenue_cagr_5yr",
    "pat_cagr_5yr",
    "eps_cagr_5yr",
]

    for col in numeric_columns:
     df[col] = pd.to_numeric(df[col], errors="coerce")

    return df

def apply_filters(df, config):

    filtered = df.copy()

    if "roe_min" in config:
        filtered = filtered[
            filtered["roe_percentage"] >= config["roe_min"]
        ]

    if "debt_to_equity_max" in config:
        filtered = filtered[
            filtered["debt_to_equity"] <= config["debt_to_equity_max"]
        ]

    if "free_cash_flow_min" in config:
        filtered = filtered[
            filtered["free_cash_flow_cr"] >= config["free_cash_flow_min"]
        ]

    if "revenue_cagr_5yr_min" in config:
        filtered = filtered[
            filtered["revenue_cagr_5yr"] >= config["revenue_cagr_5yr_min"]
        ]

    if "pat_cagr_5yr_min" in config:
        filtered = filtered[
            filtered["pat_cagr_5yr"] >= config["pat_cagr_5yr_min"]
        ]

    if "operating_profit_margin_min" in config:
        filtered = filtered[
            filtered["operating_profit_margin_pct"] >= config["operating_profit_margin_min"]
        ]

    if "asset_turnover_min" in config:
        filtered = filtered[
            filtered["asset_turnover"] >= config["asset_turnover_min"]
        ]

    if "sales_min" in config:
        filtered = filtered[
            filtered["sales"] >= config["sales_min"]
        ]

    return filtered

def normalize(series):

    p10 = series.quantile(0.10)

    p90 = series.quantile(0.90)

    clipped = series.clip(lower=p10, upper=p90)

    score = (clipped - p10) / (p90 - p10) * 100

    return score.fillna(0)

def calculate_composite_score(df):

    df = df.copy()

    df["roe_score"] = normalize(df["roe_percentage"])

    df["roce_score"] = normalize(df["roce_percentage"])

    df["npm_score"] = normalize(df["net_profit_margin_pct"])

    df["fcf_score"] = normalize(df["free_cash_flow_cr"])

    df["cfo_score"] = normalize(df["cfo_quality_score"])

    df["revenue_growth_score"] = normalize(df["revenue_cagr_5yr"])

    df["pat_growth_score"] = normalize(df["pat_cagr_5yr"])

    df["de_score"] = 100 - normalize(df["debt_to_equity"])

    df["icr_score"] = normalize(df["interest_coverage"])

    df["composite_score"] = (

        0.15 * df["roe_score"] +

        0.10 * df["roce_score"] +

        0.10 * df["npm_score"] +

        0.15 * df["fcf_score"] +

        0.10 * df["cfo_score"] +

        0.10 * df["revenue_growth_score"] +

        0.10 * df["pat_growth_score"] +

        0.10 * df["de_score"] +

        0.10 * df["icr_score"]

    )

    return df

def main():

    config = load_config()

    df = load_financial_ratios()

    df = df[
    ~df["year"].str.contains("TTM", na=False)
    ].copy()

    df["year_num"] = (
    df["year"]
    .str.extract(r"(\d{4})")
    .astype(float)
)

    df = (
    df.sort_values("year_num")
      .groupby("company_id")
      .tail(1)
      .drop(columns="year_num")
      .reset_index(drop=True)
)
    df = calculate_composite_score(df)

    quality = apply_filters(df, QUALITY_COMPOUNDER)

    value = apply_filters(df, VALUE_PICK)

    growth = apply_filters(df, GROWTH_ACCELERATOR)

    dividend = apply_filters(df, DIVIDEND_CHAMPION)

    debtfree = apply_filters(df, DEBT_FREE_BLUECHIP)

    turnaround = apply_filters(df, TURNAROUND_WATCH)

    print(config)

    print(df.head())

    

     
    print("\n===== PRESET RESULTS =====")

    print("Quality Compounder :", len(quality))
    print("Value Pick :", len(value))
    print("Growth Accelerator :", len(growth))
    print("Dividend Champion :", len(dividend))
    print("Debt Free Blue Chip :", len(debtfree))
    print("Turnaround Watch :", len(turnaround))
    print("\n===== TOP 10 COMPOSITE SCORES =====")

    print(
    df[
        [
            "company_id",
            "composite_score",
        ]
    ]
    .sort_values(
        "composite_score",
        ascending=False,
    )
    .head(10)
)
    output_folder = Path("output")

    output_folder.mkdir(exist_ok=True)

    output_file = output_folder / "screener_output.xlsx"

    with pd.ExcelWriter(output_file) as writer:

     quality.sort_values(
        "composite_score",
        ascending=False,
     ).to_excel(
        writer,
        sheet_name="Quality Compounder",
        index=False,
    )

     value.sort_values(
        "composite_score",
        ascending=False,
     ).to_excel(
        writer,
        sheet_name="Value Pick",
        index=False,
    )

     growth.sort_values(
        "composite_score",
        ascending=False,
     ).to_excel(
        writer,
        sheet_name="Growth Accelerator",
        index=False,
    )

     dividend.sort_values(
        "composite_score",
        ascending=False,
     ).to_excel(
        writer,
        sheet_name="Dividend Champion",
        index=False,
    )

     debtfree.sort_values(
        "composite_score",
        ascending=False,
     ).to_excel(
        writer,
        sheet_name="Debt Free Blue Chip",
        index=False,
    )

     turnaround.sort_values(
        "composite_score",
        ascending=False,
     ).to_excel(
        writer,
        sheet_name="Turnaround Watch",
        index=False,
    )

    print("\nExcel report generated successfully.")

    print(output_file)

if __name__ == "__main__":
    main()