from fastapi.testclient import TestClient

from src.api.main import app


client = TestClient(app)


def test_get_companies():
    response = client.get("/api/v1/companies")

    assert response.status_code == 200

    data = response.json()

    assert data["count"] == 92
    assert len(data["companies"]) == 92


def test_get_tcs():
    response = client.get("/api/v1/companies/TCS")

    assert response.status_code == 200

    data = response.json()

    assert data["company"]["id"] == "TCS"


def test_get_invalid_company():
    response = client.get("/api/v1/companies/INVALID")

    assert response.status_code == 404