import sqlite3
import pandas as pd

from src.analytics.ratios import (
    net_profit_margin,
    operating_profit_margin,
    return_on_equity,
    return_on_capital_employed,
    return_on_assets,
    debt_to_equity,
    interest_coverage_ratio,
    net_debt,
    asset_turnover,
)

from src.analytics.cagr import compute_cagr

from src.analytics.cashflow_kpis import (
    free_cash_flow,
    cfo_quality_score,
    capex_intensity,
    fcf_conversion_rate,
)


DATABASE = "data/database/nifty100.db"

def compute_cagr(values, years):
    values = [v for v in values if v is not None]

    if len(values) < years + 1:
        return None

    start = values[-(years + 1)]
    end = values[-1]

    if start <= 0 or end <= 0:
        return None

    cagr = ((end / start) ** (1 / years) - 1) * 100

    return round(cagr, 2)

def load_tables():
    """
    Load required tables from SQLite.
    """

    conn = sqlite3.connect(DATABASE)

    companies = pd.read_sql(
        "SELECT * FROM companies",
        conn
    )

    profit_loss = pd.read_sql(
        "SELECT * FROM profit_loss",
        conn
    )

    balance_sheet = pd.read_sql(
        "SELECT * FROM balance_sheet",
        conn
    )

    cash_flow = pd.read_sql(
        "SELECT * FROM cash_flow" ,
        conn
    )

    conn.close()

    return (
        companies,
        profit_loss,
        balance_sheet,
        cash_flow,
    )
def merge_tables():

    companies, profit_loss, balance_sheet, cash_flow = load_tables()

    # Remove duplicate company-year records
    profit_loss = (
        profit_loss
        .sort_values("id")
        .drop_duplicates(
            subset=["company_id", "year"],
            keep="first",
        )
    )

    balance_sheet = (
        balance_sheet
        .sort_values("id")
        .drop_duplicates(
            subset=["company_id", "year"],
            keep="first",
        )
    )

    cash_flow = (
        cash_flow
        .sort_values("id")
        .drop_duplicates(
            subset=["company_id", "year"],
            keep="first",
        )
    )

    master = profit_loss.merge(
        balance_sheet,
        on=["company_id", "year"],
        how="left",
        suffixes=("", "_bs"),
    )

    master = master.merge(
        cash_flow,
        on=["company_id", "year"],
        how="left",
        suffixes=("", "_cf"),
    )

    master = master.merge(
        companies,
        left_on="company_id",
        right_on="id",
        how="left",
        suffixes=("", "_company"),
    )

    return master
def main():

    master = merge_tables()

    


    
   
    master["net_profit_margin_pct"] = master.apply(
        lambda row: net_profit_margin(
            row["net_profit"],
            row["sales"],
        ),
        axis=1,
    )

    master["operating_profit_margin_pct"] = master.apply(
        lambda row: operating_profit_margin(
            row["operating_profit"],
            row["sales"],
        ),
        axis=1,
    )

    master["return_on_equity_pct"] = master.apply(
    lambda row: return_on_equity(
        row["net_profit"],
        row["equity_capital"],
        row["reserves"],
    ),
    axis=1,
    )

    master["return_on_capital_employed_pct"] = master.apply(
        lambda row: return_on_capital_employed(
            row["operating_profit"] + row["other_income"],
            row["equity_capital"],
            row["reserves"],
            row["borrowings"],
        ),
        axis=1,
    )

    master["return_on_assets_pct"] = master.apply(
        lambda row: return_on_assets(
            row["net_profit"],
            row["total_assets"],
        ),
        axis=1,
    )
    master["debt_to_equity"] = master.apply(
    lambda row: debt_to_equity(
        row["borrowings"],
        row["equity_capital"],
        row["reserves"],
    ),
    axis=1,
)

    master["interest_coverage"] = master.apply(
    lambda row: interest_coverage_ratio(
        row["operating_profit"],
        row["other_income"],
        row["interest"],
    ),
    axis=1,
)

    master["net_debt"] = master.apply(
    lambda row: net_debt(
        row["borrowings"],
        row["investments"],
    ),
    axis=1,
)

    master["asset_turnover"] = master.apply(
    lambda row: asset_turnover(
        row["sales"],
        row["total_assets"],
    ),
    axis=1,
)
    master["free_cash_flow_cr"] = master.apply(
    lambda row: free_cash_flow(
        row["operating_activity"],
        row["investing_activity"],
    ),
    axis=1,
)
    master[["cfo_quality_score", "cfo_quality_label"]] = master.apply(
    lambda row: pd.Series(
        cfo_quality_score(
            row["operating_activity"],
            row["net_profit"],
        )
    ),
    axis=1,
)
    master[["capex_cr", "capex_label"]] = master.apply(
    lambda row: pd.Series(
        capex_intensity(
            row["investing_activity"],
            row["sales"],
        )
    ),
    axis=1,
)
    master["fcf_conversion_rate"] = master.apply(
    lambda row: fcf_conversion_rate(
        row["free_cash_flow_cr"],
        row["operating_profit"],
    ),
    axis=1,
)
    
    
    master["revenue_cagr_5yr"] = None
    master["pat_cagr_5yr"] = None
    master["eps_cagr_5yr"] = None
    
    
    for company in master["company_id"].unique():

       
        company_df = master[
        (master["company_id"] == company)
        & (~master["year"].str.contains("TTM", na=False))
        ].copy()

    


    
        company_df["year_num"] = (
            company_df["year"]
            .str.extract(r"(\d{4})")
            .astype(float)
        )

        company_df = company_df.sort_values("year_num")
        company_df.drop(columns=["year_num"], inplace=True)

        
        

        revenue_cagr = compute_cagr(
        company_df["sales"].tolist(),
        5,
    )

        pat_cagr = compute_cagr(
        company_df["net_profit"].tolist(),
        5,
    )

        eps_cagr = compute_cagr(
        company_df["eps"].tolist(),
        5,
    )
        master.loc[
        master["company_id"] == company,
        "revenue_cagr_5yr",
        ] = revenue_cagr

        master.loc[
        master["company_id"] == company,
        "pat_cagr_5yr",
        ] = pat_cagr

        master.loc[
        master["company_id"] == company,
        "eps_cagr_5yr",
        ] = eps_cagr



    

    if company == "ABB":
        print("\n========== ABB DEBUG ==========")
        print(company_df[["year", "sales"]])
        print("Sales List:", company_df["sales"].tolist())
        print("Length:", len(company_df["sales"].tolist()))

    revenue_cagr = compute_cagr(
        company_df["sales"].tolist(),
        5,
    )

    if company == "ABB":
       print("Revenue CAGR:", revenue_cagr)

    pat_cagr = compute_cagr(
        company_df["net_profit"].tolist(),
        5,
    )

    eps_cagr = compute_cagr(
        company_df["eps"].tolist(),
        5,
    )

    master.loc[
        master["company_id"] == company,
        "revenue_cagr_5yr",
    ] = revenue_cagr

    master.loc[
        master["company_id"] == company,
        "pat_cagr_5yr",
    ] = pat_cagr

    master.loc[
        master["company_id"] == company,
        "eps_cagr_5yr",
    ] = eps_cagr

    


    
    master["composite_quality_score"] = (
    master["return_on_equity_pct"].fillna(0) * 0.30
    + master["net_profit_margin_pct"].fillna(0) * 0.20
    + master["operating_profit_margin_pct"].fillna(0) * 0.20
    + master["asset_turnover"].fillna(0) * 10 * 0.10
    + master["cfo_quality_score"].fillna(0) * 10 * 0.20

)

    master["quality_rank"] = (
    master["composite_quality_score"]
    .rank(
        ascending=False,
        method="dense",
    )
    .astype(int)
)

   

    
    import os

    os.makedirs("output", exist_ok=True)

    master[
    [
        "company_id",
        "year",
        "free_cash_flow_cr",
        "cfo_quality_score",
        "cfo_quality_label",
        "capex_cr",
        "capex_label",
        "fcf_conversion_rate",
        
    ]
    ].to_csv(
    "output/capital_allocation.csv",
    index=False,
)

    print("capital_allocation.csv created successfully.")

    edge_cases = [
    "Interest Coverage = NULL when interest expense is zero.",
    "Debt-to-Equity = NULL when shareholder equity is zero or negative.",
    "ROE = NULL when equity capital + reserves <= 0.",
    "ROCE = NULL when capital employed <= 0.",
    "ROA = NULL when total assets <= 0.",
    "Revenue CAGR = NULL when insufficient history is available.",
    "Revenue CAGR = NULL for ZERO_BASE, TURNAROUND, DECLINE_TO_LOSS and BOTH_NEGATIVE cases.",
    "FCF Conversion = NULL when operating cash flow is zero.",
]

    with open("output/ratio_edge_cases.log", "w") as f:
     for case in edge_cases:
        f.write(case + "\n")

    print("ratio_edge_cases.log created successfully.")


    conn = sqlite3.connect(DATABASE)

    print(
    master.loc[
        master["company_id"] == "ABB",
        [
            "year",
            "revenue_cagr_5yr",
            "pat_cagr_5yr",
            "eps_cagr_5yr",
        ],
    ].tail()
)

    master.to_sql(
    "financial_ratios",
    conn,
    if_exists="replace",
    index=False,
)

    cursor = conn.cursor()

    cursor.execute("""
    SELECT COUNT(*)
    FROM financial_ratios
    """)

    count = cursor.fetchone()[0]

    print("\n===== financial_ratios ROW COUNT =====")
    print(count)

    cursor.execute("""
    SELECT name
    FROM sqlite_master
    WHERE type='table';
    """)

    print(cursor.fetchall())

    conn.close()

    print("\nfinancial_ratios table updated successfully.")

    

    


if __name__ == "__main__":
  main()