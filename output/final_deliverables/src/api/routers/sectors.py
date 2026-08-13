from fastapi import APIRouter, HTTPException
import sqlite3

router = APIRouter()


DB_PATH = r"C:\Users\ashik\OneDrive\Desktop\nifty100-analytics\data\database\nifty100.db"


@router.get("/sectors")
def get_sectors():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    query = """
        SELECT
            s.broad_sector AS sector,
            COUNT(DISTINCT s.company_id) AS company_count,
            ROUND(
                (
                    SELECT AVG(x.return_on_equity_pct)
                    FROM (
                        SELECT
                            fr.company_id,
                            fr.return_on_equity_pct,
                            ROW_NUMBER() OVER (
                                PARTITION BY fr.company_id
                                ORDER BY fr.year_date DESC
                            ) AS rn
                        FROM (
                            SELECT
                                company_id,
                                return_on_equity_pct,
                                CASE
                                    WHEN year LIKE 'Mar %'
                                    THEN substr(year, 5, 4) || '-03-01'
                                    WHEN year LIKE 'Dec %'
                                    THEN substr(year, 5, 4) || '-12-01'
                                    ELSE NULL
                                END AS year_date
                            FROM financial_ratios
                        ) fr
                        WHERE fr.return_on_equity_pct IS NOT NULL
                    ) x
                    WHERE x.rn = 1
                    AND x.company_id IN (
                        SELECT company_id
                        FROM sectors
                        WHERE broad_sector = s.broad_sector
                    )
                ),
                2
            ) AS median_roe,

            NULL AS median_pe,

            ROUND(
                (
                    SELECT AVG(x.debt_to_equity)
                    FROM (
                        SELECT
                            fr.company_id,
                            fr.debt_to_equity,
                            ROW_NUMBER() OVER (
                                PARTITION BY fr.company_id
                                ORDER BY fr.year_date DESC
                            ) AS rn
                        FROM (
                            SELECT
                                company_id,
                                debt_to_equity,
                                CASE
                                    WHEN year LIKE 'Mar %'
                                    THEN substr(year, 5, 4) || '-03-01'
                                    WHEN year LIKE 'Dec %'
                                    THEN substr(year, 5, 4) || '-12-01'
                                    ELSE NULL
                                END AS year_date
                            FROM financial_ratios
                        ) fr
                        WHERE fr.debt_to_equity IS NOT NULL
                    ) x
                    WHERE x.rn = 1
                    AND x.company_id IN (
                        SELECT company_id
                        FROM sectors
                        WHERE broad_sector = s.broad_sector
                    )
                ),
                2
            ) AS median_de

        FROM sectors s
        WHERE s.broad_sector IS NOT NULL
        GROUP BY s.broad_sector
        ORDER BY s.broad_sector
    """

    rows = cursor.execute(query).fetchall()

    conn.close()

    return {
        "count": len(rows),
        "results": [dict(row) for row in rows]
    }



@router.get("/sectors/{sector}/companies")
def get_sector_companies(sector: str):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Allow IT as an alias for Information Technology
    if sector.upper() == "IT":
        sector = "Information Technology"

    # Check whether the sector exists
    sector_check = cursor.execute(
        """
        SELECT COUNT(*)
        FROM sectors
        WHERE LOWER(TRIM(broad_sector)) = LOWER(TRIM(?))
        """,
        (sector,),
    ).fetchone()[0]

    if sector_check == 0:
        conn.close()
        raise HTTPException(
            status_code=404,
            detail=f"Sector '{sector}' not found",
        )

    query = """
        WITH latest_ratios AS (
            SELECT
                fr.*,
                ROW_NUMBER() OVER (
                    PARTITION BY fr.company_id
                    ORDER BY
                        CASE
                            WHEN fr.year LIKE 'Mar %'
                                THEN substr(fr.year, 5, 4) || '-03-01'
                            WHEN fr.year LIKE 'Dec %'
                                THEN substr(fr.year, 5, 4) || '-12-01'
                            WHEN fr.year LIKE 'Sep %'
                                THEN substr(fr.year, 5, 4) || '-09-01'
                            WHEN fr.year LIKE 'Jun %'
                                THEN substr(fr.year, 5, 4) || '-06-01'
                            ELSE NULL
                        END DESC
                ) AS rn
            FROM financial_ratios fr
        )

        SELECT
            c.id AS company_id,
            c.company_name,
            s.broad_sector,
            s.sub_sector,

            lr.year,

            lr.return_on_equity_pct AS roe_pct,
            lr.return_on_capital_employed_pct AS roce_pct,
            lr.operating_profit_margin_pct,
            lr.debt_to_equity,
            lr.free_cash_flow_cr,
            lr.revenue_cagr_5yr,
            lr.pat_cagr_5yr,
            lr.eps_cagr_5yr,
            lr.net_profit_margin_pct

        FROM sectors s

        JOIN companies c
            ON c.id = s.company_id

        LEFT JOIN latest_ratios lr
            ON lr.company_id = c.id
            AND lr.rn = 1

        WHERE LOWER(TRIM(s.broad_sector))
              = LOWER(TRIM(?))

        ORDER BY c.id
    """

    rows = cursor.execute(query, (sector,)).fetchall()

    conn.close()

    return {
        "sector": sector,
        "count": len(rows),
        "results": [dict(row) for row in rows],
    }

    