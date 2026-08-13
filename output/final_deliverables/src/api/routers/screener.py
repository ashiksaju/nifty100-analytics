import sqlite3

from fastapi import APIRouter, HTTPException, Query

from src.api.config import DB_PATH


router = APIRouter()


@router.get("/screener")
def screener(
    min_roe:  str | None = Query(default=None),
    max_de: float | None = Query(default=None),
    min_fcf: float | None = Query(default=None),
    sector: str | None = Query(default=None),
    min_rev_cagr_5yr: float | None = Query(default=None),
    min_pat_cagr_5yr: float | None = Query(default=None),
    max_pe: float | None = Query(default=None),
):
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row

        query = """
    SELECT
    fr.company_id,
    c.company_name,
    s.broad_sector,
    fr.year,
    fr.operating_profit_margin_pct,
    fr.return_on_equity_pct,
    fr.debt_to_equity,
    fr.free_cash_flow_cr,
    fr.revenue_cagr_5yr,
    fr.pat_cagr_5yr
    FROM financial_ratios fr
    JOIN companies c
    ON fr.company_id = c.id
    LEFT JOIN sectors s
    ON fr.company_id = s.company_id
    WHERE fr.year NOT LIKE 'TTM'
    AND fr.year = (
    SELECT MAX(fr2.year)
    FROM financial_ratios fr2
    WHERE fr2.company_id = fr.company_id
      AND fr2.year NOT LIKE 'TTM'
)
"""
        if min_roe is not None:
            try:
                min_roe_value = float(min_roe)
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail="min_roe must be a number",
                )
        else:
            min_roe_value = None

        params = []

        if min_roe_value is not None:
            query += """
                AND CAST(return_on_equity_pct AS REAL) >= ?
            """
            params.append(min_roe_value)

        if max_de is not None:
            query += """
                AND debt_to_equity <= ?
            """
            params.append(max_de)

        if min_fcf is not None:
            query += """
                AND free_cash_flow_cr >= ?
            """
            params.append(min_fcf)

        if sector is not None:
            query += """
                AND company_id IN (
                    SELECT company_id
                    FROM sectors
                    WHERE broad_sector = ?
                )
            """
            params.append(sector)

        if min_rev_cagr_5yr is not None:
            query += """
                AND CAST(revenue_cagr_5yr AS REAL) >= ?
            """
            params.append(min_rev_cagr_5yr)

        if min_pat_cagr_5yr is not None:
            query += """
                AND CAST(pat_cagr_5yr AS REAL) >= ?
            """
            params.append(min_pat_cagr_5yr)

        # max_pe is not available in the financial_ratios table
        # yet, so only apply this filter if the column exists.
        if max_pe is not None:
            conn.close()
            raise HTTPException(
                status_code=400,
                detail="max_pe filter is not available because P/E is not present in financial_ratios."
            )

        query += """
            ORDER BY
                CAST(return_on_equity_pct AS REAL) DESC
        """

        rows = conn.execute(query, params).fetchall()

        conn.close()

        results = []

        for row in rows:
            results.append(
                {
                    "company_id": row["company_id"],
                    "company_name": row["company_name"],
                    "year": row["year"],
                    "operating_profit_margin_pct": row[
                        "operating_profit_margin_pct"
                    ],
                    "return_on_equity_pct": row[
                        "return_on_equity_pct"
                    ],
                    "debt_to_equity": row["debt_to_equity"],
                    "free_cash_flow_cr": row[
                        "free_cash_flow_cr"
                    ],
                    "revenue_cagr_5yr": row[
                        "revenue_cagr_5yr"
                    ],
                    "pat_cagr_5yr": row[
                        "pat_cagr_5yr"
                    ],
                }
            )

        return {
            "count": len(results),
            "results": results,
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )