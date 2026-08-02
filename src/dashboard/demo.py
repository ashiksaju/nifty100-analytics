import sqlite3
import pandas as pd

DATABASE = r"data/database/nifty100.db"

conn = sqlite3.connect(DATABASE)

tables = [
    "financial_ratios",
    "profit_loss",
    "balance_sheet",
    "cash_flow",
    "market_cap",
]

for table in tables:

    print("\n" + "=" * 80)
    print(table.upper())
    print("=" * 80)

    df = pd.read_sql(
        f"SELECT * FROM {table}",
        conn,
    )

    print("\nRows:", len(df))
    print("\nColumns:")
    print(df.columns.tolist())

    print("\nFirst 5 rows:")
    print(df.head())

    if "company_id" in df.columns:
        print("\nCompanies:", df["company_id"].nunique())

    if "year" in df.columns:
        print("\nYears:")
        print(sorted(df["year"].dropna().unique())[:10])
        print("...")
        print(sorted(df["year"].dropna().unique())[-10:])

print("\n" + "=" * 80)
print("CHECKING REQUIRED COLUMNS")
print("=" * 80)

ratios = pd.read_sql(
    "SELECT * FROM financial_ratios",
    conn,
)

required = [
    "roe_percentage",
    "roce_percentage",
    "revenue_cagr_5yr",
    "pat_cagr_5yr",
    "eps_cagr_5yr",
    "debt_to_equity",
    "interest_coverage",
    "operating_profit_margin_pct",
    "free_cash_flow_cr",
]

summary = []

for col in required:

    if col in ratios.columns:

        summary.append({
            "column": col,
            "non_null": ratios[col].notna().sum(),
            "null": ratios[col].isna().sum(),
        })

summary = pd.DataFrame(summary)

print(summary)

print("\n" + "=" * 80)
print("SAMPLE COMPANY HISTORY (ABB)")
print("=" * 80)

print(
    ratios.loc[
        ratios["company_id"] == "ABB"
    ].sort_values("year")
)

conn.close()