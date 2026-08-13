from pathlib import Path
import pandas as pd
import re
import sqlite3

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

analysis = pd.read_excel(
    BASE_DIR / "data" / "raw" / "analysis.xlsx",
    header=1,
)
pattern = re.compile(
    r"(\d+)\s*Years?:?\s*([\d.]+)%"
)
parsed_rows = []

failed_rows = []
metrics = [
    "compounded_sales_growth",
    "compounded_profit_growth",
    "stock_price_cagr",
    "roe",
]

for _, row in analysis.iterrows():

    company_id = row["company_id"]

    for metric in metrics:

        text = str(row[metric]).strip()

        match = pattern.search(text)

        if match:

            period = int(match.group(1))

            value = float(match.group(2))

            parsed_rows.append(
                {
                    "company_id": company_id,
                    "metric_type": metric,
                    "period_years": period,
                    "value_pct": value,
                }
            )

        else:

            failed_rows.append(
                {
                    "company_id": company_id,
                    "metric_type": metric,
                    "original_text": text,
                }
            )

            print(f"Parsed rows: {len(parsed_rows)}")
            print(f"Failed rows: {len(failed_rows)}")

            parsed_df = pd.DataFrame(parsed_rows)

            failed_df = pd.DataFrame(failed_rows)

            parsed_df.to_csv(
                OUTPUT_DIR / "analysis_parsed.csv",
                index=False,
)

            failed_df.to_csv(
                OUTPUT_DIR / "parse_failures.csv",
                index=False,
)
        

        print("analysis_parsed.csv created successfully.")

        print("parse_failures.csv created successfully.")
print(analysis.columns.tolist())
print()
print(analysis.head())
analysis = analysis.dropna(
    subset=["company_id"]
)

analysis = analysis.reset_index(
    drop=True
)
print(analysis.head())

print()

print(analysis.columns.tolist())

conn = sqlite3.connect(DATABASE)

ratio = pd.read_sql(
    """
    SELECT
        company_id,
        revenue_cagr_5yr,
        pat_cagr_5yr,
        eps_cagr_5yr
    FROM financial_ratios
    """,
    conn,
)

conn.close()

parsed_5yr = parsed_df[
    parsed_df["period_years"] == 5
].copy()

metric_map = {
    "compounded_sales_growth": "revenue_cagr_5yr",
    "compounded_profit_growth": "pat_cagr_5yr",
    "stock_price_cagr": None,
    "roe": None,
}

manual_review = []

for _, row in parsed_5yr.iterrows():

    metric = metric_map.get(row["metric_type"])

    if metric is None:
        continue

    db_row = ratio[
        ratio["company_id"] == row["company_id"]
    ]

    if db_row.empty:
        continue

    calculated = db_row.iloc[0][metric]

    if pd.isna(calculated):
     continue

    try:
      calculated = float(calculated)
    except:
      continue

    parsed_value = float(row["value_pct"])

    difference = abs(parsed_value - calculated)

    if difference > 5:

        manual_review.append(
            {
                "company_id": row["company_id"],
                "metric": row["metric_type"],
                "parsed_value": parsed_value,
                "calculated_value": calculated,
                "difference": difference,
            }
        )

manual_review_df = pd.DataFrame(manual_review)

manual_review_df.to_csv(
    OUTPUT_DIR / "manual_review.csv",
    index=False,
)

print("manual_review.csv created successfully.")