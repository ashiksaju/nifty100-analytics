import os
import sqlite3
from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse


router = APIRouter(prefix="/companies", tags=["Companies"])

DB_PATH = "data/database/nifty100.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def rows_to_dict(rows):
    return [dict(row) for row in rows]


def get_company_or_404(conn, ticker):
    company = conn.execute(
        """
        SELECT *
        FROM companies
        WHERE id = ?
        """,
        (ticker.upper(),),
    ).fetchone()

    if company is None:
        raise HTTPException(
            status_code=404,
            detail=f"Company '{ticker}' not found",
        )

    return dict(company)


def apply_year_filter(query, params, from_year, to_year):
    if from_year:
        query += " AND year >= ?"
        params.append(from_year)

    if to_year:
        query += " AND year <= ?"
        params.append(to_year)

    query += " ORDER BY year"

    return query, params


# ---------------------------------------------------------
# GET /api/v1/companies
# ---------------------------------------------------------

@router.get("")
def get_companies(
    sector: Optional[str] = Query(None),
    market_cap_category: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
):
    conn = get_connection()

    query = """
        SELECT
            c.id,
            c.company_name,
            s.broad_sector,
            s.sub_sector,
            c.roe_percentage AS roe_pct,
            c.roce_percentage AS roce_pct
        FROM companies c
        LEFT JOIN sectors s
            ON c.id = s.company_id
        WHERE 1 = 1
    """

    params = []

    if sector:
        query += """
            AND LOWER(s.broad_sector) = LOWER(?)
        """
        params.append(sector)

    if market_cap_category:
        query += """
            AND LOWER(s.market_cap_category) = LOWER(?)
        """
        params.append(market_cap_category)

    if search:
        query += """
            AND (
                LOWER(c.id) LIKE LOWER(?)
                OR LOWER(c.company_name) LIKE LOWER(?)
            )
        """
        search_value = f"%{search}%"
        params.extend([search_value, search_value])

    query += " ORDER BY c.id"

    rows = conn.execute(query, params).fetchall()

    conn.close()

    return {
        "count": len(rows),
        "companies": rows_to_dict(rows),
    }


# ---------------------------------------------------------
# GET /api/v1/companies/{ticker}
# ---------------------------------------------------------

@router.get("/{ticker}")
def get_company(ticker: str):
    conn = get_connection()

    company = get_company_or_404(conn, ticker)

    sector = conn.execute(
        """
        SELECT *
        FROM sectors
        WHERE company_id = ?
        """,
        (ticker.upper(),),
    ).fetchone()

    latest_kpis = conn.execute(
        """
        SELECT *
        FROM financial_ratios
        WHERE company_id = ?
        AND year NOT LIKE '%TTM%'
        ORDER BY
            CASE
                WHEN year LIKE 'Mar %' THEN 1
                WHEN year LIKE 'Dec %' THEN 2
                WHEN year LIKE 'Sep %' THEN 3
                WHEN year LIKE 'Jun %' THEN 4
                ELSE 5
            END,
            year DESC
        LIMIT 1
        """,
        (ticker.upper(),),
    ).fetchone()

    conn.close()

    return {
        "company": company,
        "sector": dict(sector) if sector else None,
        "latest_kpis": dict(latest_kpis) if latest_kpis else None,
    }


# ---------------------------------------------------------
# GET /api/v1/companies/{ticker}/pl
# ---------------------------------------------------------

@router.get("/{ticker}/pl")
def get_profit_loss(
    ticker: str,
    from_year: Optional[str] = Query(None),
    to_year: Optional[str] = Query(None),
):
    conn = get_connection()

    get_company_or_404(conn, ticker)

    query = """
        SELECT *
        FROM profit_loss
        WHERE company_id = ?
    """

    params = [ticker.upper()]

    query, params = apply_year_filter(
        query,
        params,
        from_year,
        to_year,
    )

    rows = conn.execute(query, params).fetchall()

    conn.close()

    return {
        "company_id": ticker.upper(),
        "history": rows_to_dict(rows),
    }


# ---------------------------------------------------------
# GET /api/v1/companies/{ticker}/bs
# ---------------------------------------------------------

@router.get("/{ticker}/bs")
def get_balance_sheet(
    ticker: str,
    from_year: Optional[str] = Query(None),
    to_year: Optional[str] = Query(None),
):
    conn = get_connection()

    get_company_or_404(conn, ticker)

    query = """
        SELECT *
        FROM balance_sheet
        WHERE company_id = ?
    """

    params = [ticker.upper()]

    query, params = apply_year_filter(
        query,
        params,
        from_year,
        to_year,
    )

    rows = conn.execute(query, params).fetchall()

    conn.close()

    return {
        "company_id": ticker.upper(),
        "history": rows_to_dict(rows),
    }


# ---------------------------------------------------------
# GET /api/v1/companies/{ticker}/cashflow
# ---------------------------------------------------------

@router.get("/{ticker}/cashflow")
def get_cash_flow(
    ticker: str,
    from_year: Optional[str] = Query(None),
    to_year: Optional[str] = Query(None),
):
    conn = get_connection()

    get_company_or_404(conn, ticker)

    query = """
        SELECT *
        FROM cash_flow
        WHERE company_id = ?
    """

    params = [ticker.upper()]

    query, params = apply_year_filter(
        query,
        params,
        from_year,
        to_year,
    )

    rows = conn.execute(query, params).fetchall()

    conn.close()

    return {
        "company_id": ticker.upper(),
        "history": rows_to_dict(rows),
    }


# ---------------------------------------------------------
# GET /api/v1/companies/{ticker}/ratios
# ---------------------------------------------------------

# GET /api/v1/companies/{ticker}/ratios
@router.get("/{ticker}/ratios")
def get_ratios(ticker: str):
    conn = get_connection()

    query = """
        SELECT *
        FROM financial_ratios
        WHERE UPPER(company_id) = UPPER(?)
        ORDER BY
            CASE
                WHEN year LIKE 'Mar %' THEN CAST(substr(year, 5, 4) AS INTEGER)
                WHEN year LIKE 'Jun %' THEN CAST(substr(year, 5, 4) AS INTEGER)
                WHEN year LIKE 'Sep %' THEN CAST(substr(year, 5, 4) AS INTEGER)
                WHEN year LIKE 'Dec %' THEN CAST(substr(year, 5, 4) AS INTEGER)
                WHEN year = 'TTM' THEN 9999
                ELSE 0
            END
    """

    rows = conn.execute(query, (ticker,)).fetchall()
    conn.close()

    return {
        "company_id": ticker.upper(),
        "count": len(rows),
        "ratios": rows_to_dict(rows),
    }

# ---------------------------------------------------------
# GET /api/v1/companies/{ticker}/tearsheet
# ---------------------------------------------------------

@router.get("/{ticker}/tearsheet")
def get_tearsheet(ticker: str):
    conn = get_connection()

    get_company_or_404(conn, ticker)

    conn.close()

    tearsheet_path = os.path.join(
        "reports",
        "tearsheets",
        f"{ticker.upper()}.pdf",
    )

    if not os.path.exists(tearsheet_path):
        raise HTTPException(
            status_code=404,
            detail=f"Tearsheet for '{ticker.upper()}' not found",
        )

    return FileResponse(
        path=tearsheet_path,
        media_type="application/pdf",
        filename=f"{ticker.upper()}_tearsheet.pdf",
    )