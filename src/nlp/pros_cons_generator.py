from pathlib import Path
import sqlite3

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

OUTPUT_DIR.mkdir(exist_ok=True)

def load_tables():

    conn = sqlite3.connect(DATABASE)

    comparison = pd.read_sql(
        "SELECT * FROM comparison_table",
        conn,
    )

    sectors = pd.read_sql(
        "SELECT * FROM sectors",
        conn,
    )

    ratios = pd.read_sql(
        "SELECT * FROM financial_ratios",
        conn,
    )

    profit_loss = pd.read_sql(
        "SELECT * FROM profit_loss",
        conn,
    )

    balance_sheet = pd.read_sql(
        "SELECT * FROM balance_sheet",
        conn,
    )

    cash_flow = pd.read_sql(
        "SELECT * FROM cash_flow",
        conn,
    )

    market_cap = pd.read_sql(
        "SELECT * FROM market_cap",
        conn,
    )

    conn.close()

    return (
        comparison,
        sectors,
        ratios,
        profit_loss,
        balance_sheet,
        cash_flow,
        market_cap,
    )

def clean_numeric(df):

    for column in df.columns:

        df[column] = pd.to_numeric(
            df[column],
            errors="ignore",
        )

    return df

def latest(df):

    return (
        df
        .sort_values("year")
        .drop_duplicates(
            subset="company_id",
            keep="last",
        )
    )

def history(df, company):

    return (
        df[
            df["company_id"] == company
        ]
        .sort_values("year")
        .reset_index(drop=True)
    )

def last_n(df, n):

    if len(df) < n:

        return None

    return df.tail(n)

def increasing(series):

    return all(
        x < y
        for x, y
        in zip(series, series[1:])
    )

def decreasing(series):

    return all(
        x > y
        for x, y
        in zip(series, series[1:])
    )

def positive(series):

    return all(
        x > 0
        for x in series
    )

def negative(series):

    return all(
        x < 0
        for x in series
    )    

def add_pro(
    company_id,
    rule_id,
    text,
    confidence,
):

    if confidence < 60:
        return

    results.append(
        {
            "company_id": company_id,
            "type": "pro",
            "rule_id": rule_id,
            "text": text,
            "confidence_pct": confidence,
        }
    )

def add_con(
    company_id,
    rule_id,
    text,
    confidence,
):

    if confidence < 60:
        return

    results.append(
        {
            "company_id": company_id,
            "type": "con",
            "rule_id": rule_id,
            "text": text,
            "confidence_pct": confidence,
        }
    )

def confidence(
    value,
    high=90,
    medium=80,
    low=70,
):

    if pd.isna(value):
        return 0

    if value >= 30:
        return high

    if value >= 20:
        return medium

    return low

results = []



def main():

    print("MAIN STARTED")

    (
        comparison,
        sectors,
        ratios,
        profit_loss,
        balance_sheet,
        cash_flow,
        market_cap,
    ) = load_tables()

    print("Tables loaded")

    ratios = clean_numeric(ratios)

    ratios_latest = latest(ratios)

    profit_loss = clean_numeric(profit_loss)
    profit_latest = latest(profit_loss)

    balance_sheet = clean_numeric(balance_sheet)
    balance_latest = latest(balance_sheet)

    cash_flow = clean_numeric(cash_flow)
    cash_latest = latest(cash_flow)

    market_cap = clean_numeric(market_cap)
    market_latest = latest(market_cap)

    financial_sectors = {
    "Banks",
    "Bank",
    "Financial Services",
    "Finance",
    "Insurance",
    "NBFC",
}

    

    for _, company in comparison.iterrows():

        print("Processing:", company["company_id"])

        company_id = company["company_id"]

        ratio = ratios_latest[
        ratios_latest["company_id"] == company_id
    ]

        if ratio.empty:
         continue

        ratio = ratio.iloc[0]
        print("Ratio loaded")

        profit = history(
        profit_loss,
        company_id,
        ).sort_values("year")

        balance = history(
        balance_sheet,
        company_id,
        ).sort_values("year")

        cash = history(
        cash_flow,
        company_id,
        ).sort_values("year")

        market = history(
        market_cap,
        company_id,
        ).sort_values("year")

        latest_profit = latest(profit)

        if not latest_profit.empty:
         latest_profit = latest_profit.iloc[0]
        latest_balance = latest(balance)
        latest_cash = latest(cash)
        latest_market = latest(market)
        print("History loaded")
        roe_history = (
        ratios[
            ratios["company_id"] == company_id
        ]
        .sort_values("year")
    )

    # ----------------------------------------------------
    # PRO 01
    # ROE >20% for last 3 years
    # ----------------------------------------------------

        last3 = roe_history.tail(3)

        if (
            len(last3) == 3
            and (last3["roe_percentage"] > 20).all()
    ):

         add_pro(
            company_id,
            "PRO_01",
            "Consistently high return on equity above 20% demonstrates exceptional capital efficiency.",
            90,
        )

    # ----------------------------------------------------
    # PRO 02
    # Positive CFO for last 5 years
    # ----------------------------------------------------

        last5_cash = cash.tail(5)

        if (
            len(last5_cash) == 5
            and (last5_cash["operating_activity"] > 0).all()
    ):

            add_pro(
                company_id,
                "PRO_02",
                "Strong free cash flow generation over 5 years signals healthy business fundamentals.",
                90,
        )

    # ----------------------------------------------------
    # PRO 03
    # Debt Free
    # ----------------------------------------------------

        if (
         pd.notna(ratio["debt_to_equity"])
         and ratio["debt_to_equity"] == 0
    ):

         add_pro(
            company_id,
            "PRO_03",
            "Debt-free balance sheet provides financial flexibility and eliminates interest burden.",
            95,
        )

    # ----------------------------------------------------
    # PRO 04
    # Revenue CAGR
    # ----------------------------------------------------

        if (
            pd.notna(ratio["revenue_cagr_5yr"])
            and ratio["revenue_cagr_5yr"] > 15
    ):

            add_pro(
                company_id,
                "PRO_04",
                "Revenue growing at above 15% CAGR over 5 years reflects strong business momentum.",
                 88,
        )

    # ----------------------------------------------------
    # PRO 05
    # OPM
    # ----------------------------------------------------

        if (
            pd.notna(ratio["operating_profit_margin_pct"])
            and ratio["operating_profit_margin_pct"] > 25
    ):

            add_pro(
                company_id,
                "PRO_05",
                "Operating profit margin above 25% indicates strong pricing power and cost discipline.",
                 85,
        )

    # ----------------------------------------------------
    # PRO 06
    # PAT CAGR
    # ----------------------------------------------------

        if (
            pd.notna(ratio["pat_cagr_5yr"])
            and ratio["pat_cagr_5yr"] > 20
    ):

            add_pro(
                company_id,
                "PRO_06",
                "Net profit compounding at above 20% over 5 years creates significant shareholder value.",
                90,
        )

            # ----------------------------------------------------
# PRO 07
# ICR > 10 OR Debt Free
# ----------------------------------------------------

        if (
    (
            pd.notna(ratio["interest_coverage"])
            and ratio["interest_coverage"] > 10
    )
        or
    (
            pd.notna(ratio["debt_to_equity"])
            and ratio["debt_to_equity"] == 0
    )
):

            add_pro(
                 company_id,
                "PRO_07",
                "Very high interest coverage ratio reflects negligible financial stress from debt servicing.",
                90,
    )



        # ----------------------------------------------------
# PRO 08
# Dividend Yield > 2% with positive FCF
# ----------------------------------------------------

        if (
             not latest_market.empty
             and pd.notna(latest_market.iloc[0]["dividend_yield_pct"])
             and latest_market.iloc[0]["dividend_yield_pct"] > 2
             and len(last5_cash) == 5
             and (last5_cash["operating_activity"] > 0).all()
):

            add_pro(
                company_id,
                "PRO_08",
                "Consistent dividend yield above 2% backed by positive free cash flow.",
                 85,
            )
        
            # ----------------------------------------------------
# PRO 09
# EPS CAGR > 15%
# ----------------------------------------------------

        if (
             pd.notna(ratio["eps_cagr_5yr"])
            and ratio["eps_cagr_5yr"] > 15
):

             add_pro(
                  company_id,
                 "PRO_09",
                "Earnings per share growing above 15% CAGR indicates strong earnings quality and compounding.",
                  88,
    )

             # ----------------------------------------------------
# PRO 10
# ROE improving for 3 consecutive years
# ----------------------------------------------------

        last3 = roe_history.tail(3)

        if (
            len(last3) == 3
            and last3["roe_percentage"].notna().all()
            and last3.iloc[0]["roe_percentage"]
             < last3.iloc[1]["roe_percentage"]
             < last3.iloc[2]["roe_percentage"]
):

            add_pro(
                company_id,
                "PRO_10",
                "Return on equity improving for 3 consecutive years shows strengthening business quality.",
                90,
    )


            # ----------------------------------------------------
# PRO 11
# PAT CAGR greater than Revenue CAGR
# (Improving operating leverage)
# ----------------------------------------------------

        if (
             pd.notna(ratio["revenue_cagr_5yr"])
            and pd.notna(ratio["pat_cagr_5yr"])
            and ratio["pat_cagr_5yr"] > ratio["revenue_cagr_5yr"]
):

            add_pro(
                company_id,
                "PRO_11",
                "Revenue growing slower than profits shows improving operating leverage and scale benefits.",
                85,
    )


    # ----------------------------------------------------
# PRO 12
# Assets growing while debt is declining
# ----------------------------------------------------

        last3_balance = balance.tail(3)

        if (
            len(last3_balance) == 3
            and last3_balance["total_assets"].notna().all()
            and last3_balance["borrowings"].notna().all()
            and (
                last3_balance.iloc[0]["total_assets"]
                < last3_balance.iloc[1]["total_assets"]
                < last3_balance.iloc[2]["total_assets"]
    )
            and (
                last3_balance.iloc[0]["borrowings"]
                > last3_balance.iloc[1]["borrowings"]
                > last3_balance.iloc[2]["borrowings"]
    )
):

            add_pro(
                 company_id,
                "PRO_12",
                "Growing asset base funded by internal accruals reflects self-sustaining growth.",
                 85,
    )

                # ----------------------------------------------------
    # CON 01
    # D/E > 2 for non-financial companies
    # ----------------------------------------------------

            financial_sectors = [
                "Banks",
                "Bank",
                "Financial Services",
                "Finance",
                "Insurance",
                "NBFC",
    ]

            sector = ""

        if "sector_name" in company.index:
            sector = str(company["sector_name"])
        elif "sector" in company.index:
            sector = str(company["sector"])
         
        sector = str(company.get("sector", ""))
        is_financial = any(
        x.lower() in sector.lower()
    for x in financial_sectors
    )

        if (
            pd.notna(ratio["debt_to_equity"])
            and ratio["debt_to_equity"] > 2
            and not is_financial
    ):

            add_con(
                company_id,
                "CON_01",
                f"Debt-to-equity ratio of {ratio['debt_to_equity']:.2f} is elevated for a non-financial company and warrants monitoring.",
                85,
        )
            

        last3_cash = cash.tail(3)
        if (
            len(last3_cash) == 3
            and (last3_cash["operating_activity"] < 0).all()
):
            add_con(
                company_id,
                "CON_02",
                "Free cash flow negative for 3 consecutive years raises concern about cash generation quality.",
                90,
    )
  


        opm_history = (
        profit
        .sort_values("year")["opm_percentage"]
        .tail(3)
)

        if (
            len(opm_history) == 3
            and opm_history.is_monotonic_decreasing
):
            add_con(
                company_id,
                "CON_03",
                "Operating margins declining for 3 consecutive years suggest pricing or cost pressure.",
                85,
    )

            if (
                pd.notna(latest_profit["net_profit"])
                and latest_profit["net_profit"] < 0
):
                add_con(
                    company_id,
                    "CON_04",
                    "Company reported a net loss in the most recent financial year.",
                    95,
    )

                # ----------------------------------------------------
# CON 05
# Revenue declining for 2 consecutive years
# ----------------------------------------------------

            sales_history = (
             profit["sales"]
            .dropna()
            .tail(3)
)

            if (
                len(sales_history) >= 3
                and sales_history.iloc[-1] < sales_history.iloc[-2]
                and sales_history.iloc[-2] < sales_history.iloc[-3]
):
                add_con(
                    company_id,
                    "CON_05",
                    "Revenue contraction over 2 consecutive years indicates demand weakness or market share loss.",
                    85,
    )

                # ----------------------------------------------------
# CON 06
# Interest Coverage Ratio < 1.5
# ----------------------------------------------------

            if (
                pd.notna(ratio["interest_coverage"])
                and ratio["interest_coverage"] < 1.5
):
                add_con(
                    company_id,
                    "CON_06",
                    "Interest coverage ratio below 1.5x indicates the company is at risk of not meeting its debt obligations.",
                    95,
    )

                # ----------------------------------------------------
# CON 07
# Dividend payout > 100%
# ----------------------------------------------------

            if (
                pd.notna(latest_profit["dividend_payout"])
                and latest_profit["dividend_payout"] > 100
):
                add_con(
                    company_id,
                    "CON_07",
                    "Dividend payout ratio above 100% means the company is paying dividends from reserves, which is unsustainable.",
                     90,
    )

                # ----------------------------------------------------
# CON 08
# Debt-to-Equity rising for 3 consecutive years
# ----------------------------------------------------

            de_history = (
            roe_history["debt_to_equity"]
            .dropna()
            .tail(3)
)

            if (
                len(de_history) == 3
                and de_history.iloc[-1] > de_history.iloc[-2]
                and de_history.iloc[-2] > de_history.iloc[-3]
):
                add_con(
                    company_id,
                    "CON_08",
                    "Rising debt-to-equity ratio over 3 years suggests increasing financial leverage risk.",
                    85,
    )

    # ----------------------------------------------------
# CON 09
# EPS declining for 3 consecutive years
# ----------------------------------------------------

            eps_history = (
            profit["eps"]
            .dropna()
            .tail(3)
)

            if (
                len(eps_history) == 3
                and eps_history.iloc[-1] < eps_history.iloc[-2]
                and eps_history.iloc[-2] < eps_history.iloc[-3]
):
                add_con(
                    company_id,
                    "CON_09",
                    "Earnings per share declining for 3 consecutive years reflects deteriorating profitability.",
                    90,
    )

    # ----------------------------------------------------
# CON 10
# ROCE < 10%
# ----------------------------------------------------

            if (
                pd.notna(ratio["roce_percentage"])
                and ratio["roce_percentage"] < 10
):
                add_con(
                    company_id,
                    "CON_10",
                    "Return on capital employed below 10% suggests the business is not generating sufficient returns on invested capital.",
                    90,
    )

                # ----------------------------------------------------
# CON 11
# Net Debt > 3x EBITDA
# ----------------------------------------------------

            if (
                pd.notna(ratio["net_debt"])
                and pd.notna(latest_profit["operating_profit"])
                and pd.notna(latest_profit["depreciation"])
):

                ebitda = (
                    latest_profit["operating_profit"]
                    + latest_profit["depreciation"]
    )

                if (
                    ebitda > 0
                    and ratio["net_debt"] > (3 * ebitda)
    ):
                    add_con(
                        company_id,
                        "CON_11",
                        "Net debt exceeding 3 times EBITDA is a high leverage ratio and limits financial flexibility.",
                        90,
        )

                # ----------------------------------------------------
# CON 12
# Revenue CAGR < 5%
# ----------------------------------------------------

            if (
                pd.notna(ratio["revenue_cagr_5yr"])
                and ratio["revenue_cagr_5yr"] < 5
):
                add_con(
                    company_id,
                    "CON_12",
                    "Revenue growing at below 5% over 5 years lags inflation and suggests limited business momentum.",
                    80,
    )

    
        print("Tables loaded successfully.")

        print()

        print("Companies :", len(comparison))

        print("Ratios :", len(ratios))

        print("Profit Loss :", len(profit_loss))

        print("Balance Sheet :", len(balance_sheet))

        print("Cash Flow :", len(cash_flow))

        print("Market Cap :", len(market_cap))

        print()

        print(ratios_latest.head())

        print()

        print(profit_latest.head())

        print()

        print(balance_latest.head())

        print()

        print(cash_latest.head())

        print()

        print(market_latest.head())
        print()

        print("\n===== RULE SUMMARY =====")

        print("Total rules generated :", len(results))

        companies_processed = set()

    for item in results:
        companies_processed.add(item["company_id"])

        print("Companies with at least one rule :", len(companies_processed))

        print("First 10 companies:")
        print(sorted(companies_processed)[:10])

        results_df = pd.DataFrame(results)

        pro_counts = (
        results_df[results_df["type"] == "pro"]
        .groupby("company_id")
        .size()
)

        con_counts = (
         results_df[results_df["type"] == "con"]
        .groupby("company_id")
        .size()
)

        all_companies = set(comparison["company_id"])

        missing_pro = sorted(all_companies - set(pro_counts.index))
        missing_con = sorted(all_companies - set(con_counts.index))

        print(f"Companies with no Pro : {len(missing_pro)}")
        print(missing_pro)

        print(f"Companies with no Con : {len(missing_con)}")
        print(missing_con)

        print(results_df.head(20))

        print()
        results_df.to_csv(
        OUTPUT_DIR / "pros_cons_generated.csv",
        index=False,
)
        summary = (
        results_df
        .groupby(["company_id", "type"])
        .size()
        .unstack(fill_value=0)
)

        print(summary.head())

        print(
        "Companies with no Pro:",
        (summary.get("pro", 0) == 0).sum()
)

        if "con" in summary.columns:
            print(
        "Companies with no Con:",
        (summary["con"] == 0).sum()
    )
        else:
         print(
        "Companies with no Con:",
        len(comparison)
    )
         print(results_df["type"].value_counts())

        print("\nUnique companies:")
        print(results_df["company_id"].nunique())

        print("\nFirst 20 rows:")
        print(results_df.head(20))

        print(f"Generated {len(results_df)} rules.")
if __name__ == "__main__":
    main()