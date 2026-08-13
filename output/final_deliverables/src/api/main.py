from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.routers import screener
from src.api.routers import sectors
from src.api.routers import valuation
from src.api.routers import portfolio
from src.api.routers import documents
import sqlite3
import time
from fastapi import Request

from src.api.routers import (
    companies,
    screener,
    sectors,
    peers,
    valuation,
    portfolio,
    documents,
    health,
)


app = FastAPI(
    title="NIFTY100 Analytics API",
    version="1.0.0",
    description="FastAPI backend for the NIFTY100 Analytics project.",
)


# --------------------------------------------------
# CORS
# --------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --------------------------------------------------
# Request Logging Middleware
# --------------------------------------------------

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()

    try:
        response = await call_next(request)

        duration = time.time() - start_time

        print(
            f"{request.method} {request.url.path} "
            f"{response.status_code} {duration:.4f}s"
        )

        return response

    except Exception as e:
        duration = time.time() - start_time

        print(
            f"ERROR {request.method} {request.url.path} "
            f"{duration:.4f}s"
        )

        print(f"Exception: {type(e).__name__}: {e}")

        raise


# --------------------------------------------------
# SQLite Connection
# --------------------------------------------------

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DB_PATH = PROJECT_ROOT / "data" / "database" / "nifty100.db"


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn



# --------------------------------------------------
# Routers
# --------------------------------------------------

app.include_router(
    companies.router,
    prefix="/api/v1",
)

app.include_router(
    screener.router,
    prefix="/api/v1",
)

app.include_router(
    sectors.router,
    prefix="/api/v1",
)

app.include_router(
    peers.router,
    prefix="/api/v1",
)

app.include_router(
    valuation.router,
    prefix="/api/v1",
)

app.include_router(
    portfolio.router,
    prefix="/api/v1",
)

app.include_router(
    documents.router,
    prefix="/api/v1",
)

app.include_router(
    health.router,
    prefix="/api/v1/health",
)


# --------------------------------------------------
# Root Endpoint
# --------------------------------------------------

@app.get("/")
def root():
    return {
        "status": "ok",
        "message": "NIFTY100 Analytics API is running",
        "version": "1.0.0",
    }