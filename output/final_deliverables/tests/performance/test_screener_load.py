import time
from concurrent.futures import ThreadPoolExecutor

from fastapi.testclient import TestClient

from src.api.main import app


def make_request():
    client = TestClient(app)

    start = time.perf_counter()

    response = client.get(
        "/api/v1/screener",
        params={"min_roe": 15},
    )

    elapsed = time.perf_counter() - start

    return response.status_code, elapsed


def test_10_concurrent_screener_calls():
    start = time.perf_counter()

    with ThreadPoolExecutor(max_workers=10) as executor:
        results = list(
            executor.map(
                lambda _: make_request(),
                range(10),
            )
        )

    total_time = time.perf_counter() - start

    assert len(results) == 10

    for status_code, response_time in results:
        assert status_code == 200

    assert total_time < 10

    print(f"\n10 concurrent requests completed in {total_time:.3f}s")

    for i, (_, response_time) in enumerate(results, 1):
        print(
            f"Request {i}: {response_time:.3f}s"
        )