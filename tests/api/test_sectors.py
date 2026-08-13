from fastapi.testclient import TestClient

from src.api.main import app


client = TestClient(app)


def test_get_sectors():
    response = client.get("/api/v1/sectors")

    assert response.status_code == 200

    data = response.json()

    sectors = data.get("sectors", data.get("results", []))

    assert len(sectors) == 10


def test_get_it_sector_companies():
    response = client.get("/api/v1/sectors/IT/companies")

    assert response.status_code == 200

    data = response.json()

    companies = data.get("companies", data.get("results", []))

    assert len(companies) > 0

    for company in companies:
        sector = company.get("broad_sector", company.get("sector"))

        if sector is not None:
            assert sector.upper() == "INFORMATION TECHNOLOGY"