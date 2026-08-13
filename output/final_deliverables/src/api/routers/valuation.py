from fastapi import APIRouter, HTTPException
import sqlite3

router = APIRouter()

DB_PATH = r"C:\Users\ashik\OneDrive\Desktop\nifty100-analytics\data\database\nifty100.db"


@router.get("/market-cap/{ticker}")
def get_market_cap_history(ticker: str):

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # ---------------------------------------------------------
    # Check company exists
    # ---------------------------------------------------------

    company = cursor.execute(
        """
        SELECT
            id,
            company_name
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

    # ---------------------------------------------------------
    # Get market-cap history
    # ---------------------------------------------------------

    rows = cursor.execute(
        """
        SELECT
            company_id,
            year,
            market_cap_crore,
            enterprise_value_crore,
            pe_ratio,
            pb_ratio,
            ev_ebitda,
            dividend_yield_pct
        FROM market_cap
        WHERE UPPER(company_id) = UPPER(?)
          AND year BETWEEN 2019 AND 2024
        ORDER BY year
        """,
        (ticker,)
    ).fetchall()

    conn.close()

    if not rows:
        raise HTTPException(
            status_code=404,
            detail=f"No market-cap data found for '{ticker}'"
        )

    # ---------------------------------------------------------
    # Return response
    # ---------------------------------------------------------

    return {
        "company_id": company["id"],
        "company_name": company["company_name"],
        "from_year": 2019,
        "to_year": 2024,
        "count": len(rows),
        "history": [
            {
                "year": row["year"],
                "market_cap_crore": row["market_cap_crore"],
                "enterprise_value_crore": row["enterprise_value_crore"],
                "pe_ratio": row["pe_ratio"],
                "pb_ratio": row["pb_ratio"],
                "ev_ebitda": row["ev_ebitda"],
                "dividend_yield_pct": row["dividend_yield_pct"]
            }
            for row in rows
        ]
    }