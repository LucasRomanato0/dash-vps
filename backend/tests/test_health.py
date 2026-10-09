from fastapi.testclient import TestClient

from app.config import get_settings
from app.main import app


def test_health_returns_stable_payload_and_initializes_database(tmp_path, monkeypatch):
    database_path = tmp_path / "health.db"
    monkeypatch.setenv("DASH_VPS_DATABASE_PATH", str(database_path))
    get_settings.cache_clear()

    with TestClient(app) as client:
        response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "dash-vps-api",
        "database": "sqlite",
    }
    assert database_path.is_file()
    get_settings.cache_clear()
