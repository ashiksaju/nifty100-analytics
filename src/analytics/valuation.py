import sqlite3
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[2]

DATABASE = (
    BASE_DIR
    / "data"
    / "database"
    / "nifty100.db"
)

OUTPUT_DIR = (
    BASE_DIR
    / "output"
)

OUTPUT_DIR.mkdir(
    exist_ok=True,
)

conn = sqlite3.connect(DATABASE)

valuation = pd.read_sql(
    """
    SELECT
        c.company_id,
        c.company_name,
        s.broad_sector,
        f.free_cash_flow_cr,
        m.market_cap_crore,
        m.pe_ratio,
        m.pb_ratio,
        m.ev_ebitda
    FROM comparison_table c
    JOIN sectors s
        ON c.company_id = s.company_id
    JOIN market_cap m
        ON c.company_id = m.company_id
    JOIN financial_ratios f
        ON c.company_id = f.company_id
    """,
    conn,
)

conn.close()

# Keep one record per company
valuation = (
    valuation
    .sort_values("company_id")
    .drop_duplicates(
        subset="company_id",
        keep="last",
    )
)

# FCF Yield
valuation["FCF_yield_pct"] = (
    valuation["free_cash_flow_cr"]
    / valuation["market_cap_crore"]
) * 100


sector_pe = (
    valuation
    .groupby("broad_sector")["pe_ratio"]
    .median()
    .reset_index()
)

sector_pe.columns = [
    "broad_sector",
    "sector_median_pe",
]

# Merge Sector Median
valuation = valuation.merge(
    sector_pe,
    on="broad_sector",
    how="left",
)

valuation["PE_vs_sector_median_pct"] = (
    valuation["pe_ratio"]
    / valuation["sector_median_pe"]
) * 100

valuation["flag"] = "Fair"

valuation.loc[
    valuation["pe_ratio"]
    > valuation["sector_median_pe"] * 1.5,
    "flag",
] = "Caution"

valuation.loc[
    valuation["pe_ratio"]
    < valuation["sector_median_pe"] * 0.7,
    "flag",
] = "Discount"


valuation_summary = valuation[
    [
        "company_id",
        "company_name",
        "broad_sector",
        "pe_ratio",
        "pb_ratio",
        "ev_ebitda",
        "FCF_yield_pct",
        "sector_median_pe",
        "PE_vs_sector_median_pct",
        "flag",
    ]
].copy()

valuation_summary.rename(
    columns={
        "broad_sector": "sector",
        "sector_median_pe": "5yr_median_PE",
    },
    inplace=True,
)

valuation_summary.to_excel(
    OUTPUT_DIR / "valuation_summary.xlsx",
    index=False,
)

valuation_flags = valuation_summary[
    valuation_summary["flag"] != "Fair"
].copy()

valuation_flags.to_csv(
    OUTPUT_DIR / "valuation_flags.csv",
    index=False,
)

print("valuation_summary.xlsx created successfully.")
print("valuation_flags.csv created successfully.")