from fastapi.testclient import TestClient

from src.api.main import app


client = TestClient(app)


def test_screener_min_roe():
    response = client.get(
        "/api/v1/screener",
        params={"min_roe": 15},
    )

    assert response.status_code == 200

    data = response.json()

    results = data.get("results", data.get("companies", []))

    for company in results:
        roe = company.get("roe_pct", company.get("roe_percentage"))

        if roe is not None:
            assert roe >= 15


def test_screener_invalid_parameter():
    response = client.get(
        "/api/v1/screener",
        params={"min_roe": "invalid"},
    )

    assert response.status_code == 400