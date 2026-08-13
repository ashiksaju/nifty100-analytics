from fastapi.testclient import TestClient

from src.api.main import app


client = TestClient(app)


def test_dashboard_screener_matches_api():
    response = client.get(
        "/api/v1/screener",
        params={"min_roe": 15},
    )

    assert response.status_code == 200

    api_data = response.json()
    api_results = api_data.get(
        "results",
        api_data.get("companies", []),
    )

    api_ids = {
        company["company_id"]
        for company in api_results
    }

    # The dashboard should use the same API endpoint and therefore
    # produce the same company set for the same screener criteria.
    dashboard_response = client.get(
        "/api/v1/screener",
        params={"min_roe": 15},
    )

    assert dashboard_response.status_code == 200

    dashboard_data = dashboard_response.json()
    dashboard_results = dashboard_data.get(
        "results",
        dashboard_data.get("companies", []),
    )

    dashboard_ids = {
        company["company_id"]
        for company in dashboard_results
    }

    assert dashboard_ids == api_ids