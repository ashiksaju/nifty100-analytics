from fastapi import APIRouter, HTTPException
import sqlite3

router = APIRouter()

DB_PATH = r"C:\Users\ashik\OneDrive\Desktop\nifty100-analytics\data\database\nifty100.db"


@router.get("/peers/{group_name}")
def get_peer_group(group_name: str):

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # ---------------------------------------------------------
    # Check whether peer group exists
    # ---------------------------------------------------------

    group = cursor.execute(
        """
        SELECT DISTINCT peer_group_name
        FROM peer_groups
        WHERE LOWER(TRIM(peer_group_name)) = LOWER(TRIM(?))
        """,
        (group_name,)
    ).fetchone()

    if not group:
        conn.close()

        raise HTTPException(
            status_code=404,
            detail=f"Peer group '{group_name}' not found"
        )

    actual_group_name = group["peer_group_name"]

    # ---------------------------------------------------------
    # Get companies + percentile data
    # ---------------------------------------------------------

    rows = cursor.execute(
        """
        SELECT
            pg.company_id,
            c.company_name,
            pg.peer_group_name,
            pg.is_benchmark,

            pp.asset_turnover_percentile,
            pp.debt_to_equity_percentile,
            pp.eps_cagr_5yr_percentile,
            pp.free_cash_flow_cr_percentile,
            pp.interest_coverage_percentile,
            pp.net_profit_margin_pct_percentile,
            pp.pat_cagr_5yr_percentile,
            pp.revenue_cagr_5yr_percentile,
            pp.roce_percentage_percentile,
            pp.roe_percentage_percentile

        FROM peer_groups pg

        LEFT JOIN companies c
            ON c.id = pg.company_id

        LEFT JOIN peer_percentiles pp
            ON pp.company_id = pg.company_id

        WHERE LOWER(TRIM(pg.peer_group_name))
              = LOWER(TRIM(?))

        ORDER BY
            pg.is_benchmark DESC,
            pg.company_id
        """,
        (actual_group_name,)
    ).fetchall()

    conn.close()

    # ---------------------------------------------------------
    # Return response
    # ---------------------------------------------------------

    return {
        "peer_group": actual_group_name,
        "count": len(rows),
        "results": [
            dict(row)
            for row in rows
        ]
    }

@router.get("/companies/{ticker}/peers/compare")
def compare_company_with_peers(ticker: str):

    import sqlite3
    from fastapi import HTTPException

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # ---------------------------------------------------------
    # Find company
    # ---------------------------------------------------------

    company = cursor.execute(
        """
        SELECT id, company_name
        FROM companies
        WHERE UPPER(id) = UPPER(?)
        """,
        (ticker,)
    ).fetchone()

    if not company:
        conn.close()
        raise HTTPException(
            status_code=404,
            detail=f"Company '{ticker}' not found"
        )

    company_id = company["id"]

    # ---------------------------------------------------------
    # Find peer group
    # ---------------------------------------------------------

    peer_group = cursor.execute(
        """
        SELECT peer_group_name
        FROM peer_groups
        WHERE UPPER(company_id) = UPPER(?)
        LIMIT 1
        """,
        (company_id,)
    ).fetchone()

    if not peer_group:
        conn.close()
        raise HTTPException(
            status_code=404,
            detail=f"No peer group found for '{ticker}'"
        )

    group_name = peer_group["peer_group_name"]

    # ---------------------------------------------------------
    # Find benchmark company
    # ---------------------------------------------------------

    benchmark = cursor.execute(
        """
        SELECT company_id
        FROM peer_groups
        WHERE peer_group_name = ?
          AND is_benchmark = 1
        LIMIT 1
        """,
        (group_name,)
    ).fetchone()

    if not benchmark:
        conn.close()
        raise HTTPException(
            status_code=404,
            detail=f"No benchmark found for peer group '{group_name}'"
        )

    benchmark_id = benchmark["company_id"]

    # ---------------------------------------------------------
    # Metrics used for radar comparison
    # ---------------------------------------------------------

    metrics = {
        "ROE": "roe_percentage_percentile",
        "ROCE": "roce_percentage_percentile",
        "Debt to Equity": "debt_to_equity_percentile",
        "Revenue CAGR": "revenue_cagr_5yr_percentile",
        "PAT CAGR": "pat_cagr_5yr_percentile",
        "EPS CAGR": "eps_cagr_5yr_percentile",
        "FCF": "free_cash_flow_cr_percentile",
        "Net Profit Margin": "net_profit_margin_pct_percentile"
    }

    # ---------------------------------------------------------
    # Get percentile data
    # ---------------------------------------------------------

    peer_rows = cursor.execute(
        """
        SELECT
            pg.company_id,
            pg.is_benchmark,
            pp.roe_percentage_percentile,
            pp.roce_percentage_percentile,
            pp.debt_to_equity_percentile,
            pp.revenue_cagr_5yr_percentile,
            pp.pat_cagr_5yr_percentile,
            pp.eps_cagr_5yr_percentile,
            pp.free_cash_flow_cr_percentile,
            pp.net_profit_margin_pct_percentile

        FROM peer_groups pg

        LEFT JOIN peer_percentiles pp
            ON pp.company_id = pg.company_id

        WHERE pg.peer_group_name = ?
        """,
        (group_name,)
    ).fetchall()

    # ---------------------------------------------------------
    # Convert SQLite rows to dictionaries
    # ---------------------------------------------------------

    peer_data = [dict(row) for row in peer_rows]

    # ---------------------------------------------------------
    # Find selected company
    # ---------------------------------------------------------

    selected = None

    for row in peer_data:
        if row["company_id"].upper() == company_id.upper():
            selected = row
            break

    if not selected:
        conn.close()
        raise HTTPException(
            status_code=404,
            detail=f"Percentile data not found for '{ticker}'"
        )

    # ---------------------------------------------------------
    # Find benchmark
    # ---------------------------------------------------------

    benchmark_data = None

    for row in peer_data:
        if row["company_id"].upper() == benchmark_id.upper():
            benchmark_data = row
            break

    # ---------------------------------------------------------
    # Build radar data
    # ---------------------------------------------------------

    radar = []

    for label, column in metrics.items():

        values = []

        for row in peer_data:

            value = row[column]

            if value is not None:

                try:
                    values.append(float(value))
                except (ValueError, TypeError):
                    pass

        peer_average = (
            sum(values) / len(values)
            if values
            else None
        )

        radar.append(
            {
                "metric": label,
                "company": selected[column],
                "peer_group_average": peer_average,
                "benchmark": (
                    benchmark_data[column]
                    if benchmark_data
                    else None
                )
            }
        )

    conn.close()

    return {
        "company": {
            "ticker": company_id,
            "name": company["company_name"]
        },
        "peer_group": group_name,
        "benchmark_company": benchmark_id,
        "radar_data": radar
    }