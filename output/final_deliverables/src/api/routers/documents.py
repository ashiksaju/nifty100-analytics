from fastapi import APIRouter, HTTPException
import sqlite3
import re
from urllib.parse import urlparse
from urllib.request import Request, urlopen

router = APIRouter()

DB_PATH = r"C:\Users\ashik\OneDrive\Desktop\nifty100-analytics\data\database\nifty100.db"


def clean_url(value):
    """
    Convert Markdown-style URLs into normal URLs.
    """

    if not value:
        return None

    value = str(value).strip()

    # Format:
    # [https://example.com/file.pdf](https://example.com/file.pdf)

    match = re.match(r"\[([^\]]+)\]\(([^)]+)\)", value)

    if match:
        return match.group(2)

    # Remove accidental surrounding brackets
    value = value.strip("[]() ")

    return value


def check_url(url):
    """
    Check whether a URL is reachable.
    Returns True or False.
    """

    if not url:
        return False

    try:

        parsed = urlparse(url)

        if parsed.scheme not in ("http", "https"):
            return False

        request = Request(
            url,
            method="HEAD",
            headers={
                "User-Agent": "Mozilla/5.0"
            }
        )

        with urlopen(
            request,
            timeout=5
        ) as response:

            return 200 <= response.status < 400

    except Exception:

        # Some servers reject HEAD requests.
        # Try a normal GET request.

        try:

            request = Request(
                url,
                headers={
                    "User-Agent": "Mozilla/5.0"
                }
            )

            with urlopen(
                request,
                timeout=5
            ) as response:

                return 200 <= response.status < 400

        except Exception:

            return False


@router.get("/companies/{ticker}/documents")
def get_company_documents(ticker: str):

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
    # Get annual reports
    # ---------------------------------------------------------

    rows = cursor.execute(
        """
        SELECT
            Year,
            Annual_Report
        FROM documents
        WHERE UPPER(company_id) = UPPER(?)
        ORDER BY Year DESC
        """,
        (ticker,)
    ).fetchall()

    conn.close()

    # ---------------------------------------------------------
    # Build response
    # ---------------------------------------------------------

    documents = []

    for row in rows:

        url = clean_url(row["Annual_Report"])

        documents.append(
            {
                "year": row["Year"],
                "annual_report": url,
                "is_url_valid": check_url(url)
            }
        )

    return {
        "company_id": company["id"],
        "company_name": company["company_name"],
        "count": len(documents),
        "documents": documents
    }