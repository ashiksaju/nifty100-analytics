from fastapi import APIRouter
import sqlite3
import math

router = APIRouter()

DB_PATH = r"C:\Users\ashik\OneDrive\Desktop\nifty100-analytics\data\database\nifty100.db"


@router.get("/portfolio/stats")
def get_portfolio_stats():

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    kpis = {
        "asset_turnover": "Asset Turnover",
        "debt_to_equity": "Debt to Equity",
        "eps_cagr_5yr": "EPS CAGR 5Y",
        "free_cash_flow_cr": "Free Cash Flow (Cr)",
        "interest_coverage": "Interest Coverage",
        "net_profit_margin_pct": "Net Profit Margin %",
        "pat_cagr_5yr": "PAT CAGR 5Y",
        "revenue_cagr_5yr": "Revenue CAGR 5Y",
        "roce_percentage": "ROCE %",
        "roe_percentage": "ROE %"
    }

    query = """
        WITH ranked_ratios AS (
            SELECT
                fr.*,

                ROW_NUMBER() OVER (
                    PARTITION BY fr.company_id
                    ORDER BY
                        CASE
                            WHEN fr.year = 'TTM' THEN 999999
                            WHEN fr.year LIKE 'Mar %'
                                THEN CAST(substr(fr.year, 5, 4) AS INTEGER)
                            WHEN fr.year LIKE 'Dec %'
                                THEN CAST(substr(fr.year, 5, 4) AS INTEGER)
                            ELSE 0
                        END DESC,
                        fr.id DESC
                ) AS rn

            FROM financial_ratios fr
        )

        SELECT
            c.id AS company_id,
            c.company_name,

            fr.asset_turnover,
            fr.debt_to_equity,
            fr.eps_cagr_5yr,
            fr.free_cash_flow_cr,
            fr.interest_coverage,
            fr.net_profit_margin_pct,
            fr.pat_cagr_5yr,
            fr.revenue_cagr_5yr,
            fr.roce_percentage,
            fr.roe_percentage

        FROM companies c

        LEFT JOIN ranked_ratios fr
            ON fr.company_id = c.id
            AND fr.rn = 1

        ORDER BY c.id
    """

    rows = cursor.execute(query).fetchall()

    conn.close()

    data = []

    for row in rows:

        company_data = {}

        for column in kpis:

            value = row[column]

            if value is None:
                company_data[column] = None
                continue

            try:
                value = float(value)

                if math.isnan(value) or math.isinf(value):
                    company_data[column] = None
                else:
                    company_data[column] = value

            except (ValueError, TypeError):
                company_data[column] = None

        data.append(company_data)

    def percentile(values, percentile_value):

        if not values:
            return None

        values = sorted(values)

        if len(values) == 1:
            return values[0]

        position = (
            (len(values) - 1)
            * percentile_value
            / 100
        )

        lower = int(math.floor(position))
        upper = int(math.ceil(position))

        if lower == upper:
            return values[lower]

        weight = position - lower

        return (
            values[lower]
            + (values[upper] - values[lower])
            * weight
        )

    statistics = []

    for column, display_name in kpis.items():

        values = [
            row[column]
            for row in data
            if row[column] is not None
        ]

        statistics.append(
            {
                "kpi": column,
                "label": display_name,
                "count": len(values),
                "p10": round(percentile(values, 10), 2)
                if values else None,
                "p25": round(percentile(values, 25), 2)
                if values else None,
                "p50": round(percentile(values, 50), 2)
                if values else None,
                "p75": round(percentile(values, 75), 2)
                if values else None,
                "p90": round(percentile(values, 90), 2)
                if values else None
            }
        )

    return {
        "company_count": len(data),
        "kpi_count": len(kpis),
        "statistics": statistics
    }