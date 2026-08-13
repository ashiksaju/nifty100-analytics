import subprocess
import sys
import time

import requests


def test_fastapi_and_streamlit_run_together():
    fastapi = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "src.api.main:app",
            "--host",
            "127.0.0.1",
            "--port",
            "8000",
        ]
    )

    streamlit = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "streamlit",
            "run",
            "src/dashboard/app.py",
            "--server.address",
            "127.0.0.1",
            "--server.port",
            "8501",
            "--server.headless",
            "true",
        ]
    )

    try:
        time.sleep(5)

        fastapi_response = requests.get(
            "http://127.0.0.1:8000/api/v1/health",
            timeout=5,
        )

        streamlit_response = requests.get(
            "http://127.0.0.1:8501",
            timeout=5,
        )

        assert fastapi_response.status_code == 200
        assert streamlit_response.status_code == 200

        health_data = fastapi_response.json()

        assert health_data["status"] == "ok"

        print("\nFastAPI: port 8000 OK")
        print("Streamlit: port 8501 OK")
        print("Both services running simultaneously: PASS")

    finally:
        streamlit.terminate()
        fastapi.terminate()

        streamlit.wait(timeout=10)
        fastapi.wait(timeout=10)