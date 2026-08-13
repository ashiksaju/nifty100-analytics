from fastapi import APIRouter
import sqlite3
import time
from pathlib import Path

router = APIRouter()

START_TIME = time.time()

DB_PATH = Path("data/database/nifty100.db")

VERSION = "1.0.0"


@router.get("")
def health_check():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    tables = [
        "profit_loss",
        "balance_sheet",
        "cash_flow",
        "analysis",
        "documents",
        "pros_cons",
        "financial_ratios",
        "market_cap",
        "peer_groups",
        "sectors",
    ]

    db_row_counts = {}

    for table in tables:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            db_row_counts[table] = cursor.fetchone()[0]
        except sqlite3.Error:
            db_row_counts[table] = None

    conn.close()

    return {
        "status": "ok",
        "db_row_counts": db_row_counts,
        "uptime_seconds": round(time.time() - START_TIME, 2),
        "version": VERSION,
    }