import time

from fastapi.testclient import TestClient

from src.api.main import app


client = TestClient(app)


def test_company_profile_load_time():
    tickers = [
        "TCS",
        "INFY",
        "HCLTECH",
        "LTIM",
        "TECHM",
    ]

    for ticker in tickers:
        start = time.perf_counter()

        response = client.get(
            f"/api/v1/companies/{ticker}"
        )

        elapsed = time.perf_counter() - start

        assert response.status_code == 200

        print(
            f"\n{ticker} Company Profile API load time: "
            f"{elapsed:.3f}s"
        )

        assert elapsed < 3