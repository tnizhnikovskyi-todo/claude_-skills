from fastapi.testclient import TestClient

from billing.main import app


def test_app_starts() -> None:
    client = TestClient(app)
    assert client.get("/docs").status_code == 200
