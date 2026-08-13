import pandas as pd
import numpy as np
import sqlite3
from pathlib import Path




def free_cash_flow(operating_activity, investing_activity):
    """
    Free Cash Flow (FCF)

    Formula:
        Operating Activity + Investing Activity

    Note:
        Investing Activity is usually negative.
        Negative FCF is allowed.
    """

    return operating_activity + investing_activity
def cfo_quality_score(cfo, pat):
    """
    CFO Quality Score

    Formula:
        CFO / PAT

    Returns:
        (ratio, label)

    Labels:
        High Quality
        Moderate
        Accrual Risk
    """

    if pat == 0:
        return None, None

    ratio = cfo / pat

    if ratio > 1.0:
        label = "High Quality"
    elif ratio >= 0.5:
        label = "Moderate"
    else:
        label = "Accrual Risk"

    return ratio, label
def capex_intensity(investing_activity, sales):
    """
    CapEx Intensity

    Formula:
        abs(Investing Activity) / Sales * 100

    Returns:
        (percentage, label)
    """

    if sales == 0:
        return None, None

    percentage = abs(investing_activity) / sales * 100

    if percentage < 3:
        label = "Asset Light"
    elif percentage <= 8:
        label = "Moderate"
    else:
        label = "Capital Intensive"

    return percentage, label
def fcf_conversion_rate(free_cash_flow, operating_profit):
    """
    FCF Conversion Rate

    Formula:
        FCF / Operating Profit * 100

    Returns:
        None if operating_profit is 0.
    """

    if operating_profit == 0:
        return None

    return (free_cash_flow / operating_profit) * 100

def capital_allocation_pattern(
    cfo,
    cfi,
    cff,
    cfo_pat_ratio=None,
    capex_label=None,
):
    """
    Classify capital allocation pattern based on
    CFO, CFI and CFF signs.
    """

    cfo_positive = cfo >= 0
    cfi_positive = cfi >= 0
    cff_positive = cff >= 0

    if cfo_positive and not cfi_positive and not cff_positive:
        if cfo_pat_ratio is not None and cfo_pat_ratio > 1.0:
            return "Shareholder Returns"
        return "Reinvestor"

    if cfo_positive and cfi_positive and not cff_positive:
        if capex_label == "Asset Light":
            return "Shareholder Returns"
        return "Liquidating Assets"

    if not cfo_positive and cfi_positive and cff_positive:
        return "Distress Signal"

    if not cfo_positive and not cfi_positive and cff_positive:
        return "Growth Funded by Debt"

    if cfo_positive and cfi_positive and cff_positive:
        return "Cash Accumulator"

    if not cfo_positive and not cfi_positive and not cff_positive:
        return "Pre-Revenue"

    if cfo_positive and not cfi_positive and cff_positive:
        return "Mixed"

    return "Unknown"

# ----------------------------------------------------
# MAIN
# ----------------------------------------------------

def main():

    BASE_DIR = Path(__file__).resolve().parents[2]

    DB_PATH = BASE_DIR / "data"/"database" / "nifty100.db"

    OUTPUT_DIR = BASE_DIR / "output"
    OUTPUT_DIR.mkdir(exist_ok=True)

    conn = sqlite3.connect(DB_PATH)

    cursor = conn.cursor()

    cursor.execute(
    "SELECT name FROM sqlite_master WHERE type='table';"
)
    
    
   

    profit_loss = pd.read_sql(
        "SELECT * FROM profit_loss",
        conn,
    )

    comparison = pd.read_sql(
    "SELECT * FROM comparison_table",
    conn,
)
    
    sectors = pd.read_sql(
    "SELECT * FROM sectors",
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
    capital_allocation = pd.read_csv(
    OUTPUT_DIR / "capital_allocation.csv"
)
    print("Rows :", len(capital_allocation))

    print("Companies :", capital_allocation["company_id"].nunique())
    print(capital_allocation.columns.tolist())

    print(capital_allocation.head())

    print("Tables loaded")

    results = []
    distress = []
    pattern_changes = []

    for _, company in comparison.iterrows():

        company_id = company["company_id"]

        sector_row = sectors[
        sectors["company_id"] == company_id
]

        if sector_row.empty:
            sector = "Unknown"
        else:
            sector = sector_row.iloc[0]["broad_sector"]

        profit = (
            profit_loss[
                profit_loss["company_id"] == company_id
            ]
            .sort_values("year")
        )

        cash = (
            cash_flow[
                cash_flow["company_id"] == company_id
            ]
            .sort_values("year")
        )

        balance = (
            balance_sheet[
                balance_sheet["company_id"] == company_id
            ]
            .sort_values("year")
        )

        if (
            profit.empty
            or cash.empty
            or balance.empty
        ):
            continue

        latest_profit = profit.iloc[-1]

        latest_cash = cash.iloc[-1]

        latest_balance = balance.iloc[-1]

        # ----------------------------------------
        # Cash Flow KPIs
        # ----------------------------------------

        fcf = free_cash_flow(
            latest_cash["operating_activity"],
            latest_cash["investing_activity"],
        )

        cfo_score, cfo_label = cfo_quality_score(
            latest_cash["operating_activity"],
            latest_profit["net_profit"],
        )

        capex_pct, capex_label = capex_intensity(
            latest_cash["investing_activity"],
            latest_profit["sales"],
        )

        fcf_conversion = fcf_conversion_rate(
            fcf,
            latest_profit["operating_profit"],
        )

        capital_label = capital_allocation_pattern(
            latest_cash["operating_activity"],
            latest_cash["investing_activity"],
            latest_cash["financing_activity"],
            cfo_score,
            capex_label,
        )

                # ----------------------------------------
        # Distress & Deleveraging
        # ----------------------------------------

        distress_flag = (
            latest_cash["operating_activity"] < 0
            and latest_cash["financing_activity"] > 0
        )

        deleveraging_flag = False

        if len(balance) >= 2:

            previous_balance = balance.iloc[-2]

            if (
                latest_cash["financing_activity"] < 0
                and latest_balance["borrowings"]
                < previous_balance["borrowings"]
            ):
                deleveraging_flag = True

        # ----------------------------------------
        # FCF CAGR (5 Year)
        # ----------------------------------------

        cash = cash.copy()

        cash["fcf"] = (
            cash["operating_activity"]
            + cash["investing_activity"]
        )

        fcf_cagr = None

        if len(cash) >= 5:

            first = cash.iloc[-5]["fcf"]
            last = cash.iloc[-1]["fcf"]

            if (
                first > 0
                and last > 0
            ):
                fcf_cagr = (
                    ((last / first) ** (1 / 4) - 1)
                    * 100
                )

                previous_pattern = None

            if len(cash) >= 2:

                previous_cash = cash.iloc[-2]

                previous_profit = profit.iloc[-2]

                previous_ratio, _ = cfo_quality_score(
                previous_cash["operating_activity"],
                previous_profit["net_profit"],
    )

                previous_pattern = capital_allocation_pattern(
                previous_cash["operating_activity"],
                previous_cash["investing_activity"],
                previous_cash["financing_activity"],
                previous_ratio,
    )


                results.append(

                    
            {
                "company_id": company_id,
                "sector": sector,
                "cfo_quality_score": cfo_score,
                "cfo_quality_label": cfo_label,
                "capex_intensity_pct": capex_pct,
                "capex_label": capex_label,
                "fcf_cagr_5yr": fcf_cagr,
                "fcf_conversion_pct": fcf_conversion,
                "distress_flag": distress_flag,
                "deleveraging_flag": deleveraging_flag,
                "capital_allocation_label": capital_label,
            }
        )
                if (
                    previous_pattern is not None
                    and previous_pattern != capital_label
):

                    pattern_changes.append(
        {
                     "company_id": company_id,
                     "previous_pattern": previous_pattern,
                     "current_pattern": capital_label,
        }
    )

        if distress_flag:

            distress.append(
                {
                    "company_id": company_id,
                    "cfo": latest_cash["operating_activity"],
                    "cff": latest_cash["financing_activity"],
                    "latest_net_profit": latest_profit["net_profit"],
                }
            )

    results_df = pd.DataFrame(results)

    distress_df = pd.DataFrame(distress)

    pattern_changes_df = pd.DataFrame(pattern_changes)

    pattern_changes_df.to_csv(
    OUTPUT_DIR / "pattern_changes.csv",
    index=False,
)

    distribution = (
    results_df["capital_allocation_label"]
    .value_counts()
    .reset_index()
)

    distribution.columns = [
    "capital_allocation_label",
    "company_count",
]

    distribution.to_csv(
    OUTPUT_DIR / "capital_allocation_distribution.csv",
    index=False,
)

    print("\nCapital Allocation Distribution")
    print(distribution)

    results_df.to_excel(
            OUTPUT_DIR / "cashflow_intelligence.xlsx",
            index=False,
    )

    distress_df.to_csv(
             OUTPUT_DIR / "distress_alerts.csv",
            index=False,
    )

    print()
    print("Cash Flow Intelligence Generated")
    print(results_df.head())

    print()
    print("Total Companies :", len(results_df))
    print("Distress Alerts :", len(distress_df))


if __name__ == "__main__":
    main()