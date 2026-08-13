from fastapi.testclient import TestClient

from src.api.main import app


client = TestClient(app)


def test_health_endpoint():
    response = client.get("/api/v1/health")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "ok"

    assert "db_row_counts" in data

    expected_tables = {
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
}

    assert expected_tables.issubset(
        set(data["db_row_counts"].keys())
    )