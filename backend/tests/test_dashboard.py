from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient

from app.config import get_settings
from app.main import app


def sample(at, cpu=20):
    return {
        "collected_at": at.isoformat(), "hostname": "vps-test",
        "cores": 4, "ram_gb": 8, "disk_gb": 80, "os": "Linux", "region": "BR",
        "cpu_percent": cpu, "memory_percent": 40, "disk_percent": 50,
        "load_1m": 0.5, "uptime_seconds": 100,
        "containers": {"running": 1, "stopped": 0, "exited": 0, "restarting": 0},
        "services": [{"name": "app", "description": "teste", "online": True, "latency_ms": 10}],
        "alerts": [{"priority": "info", "title": "coleta", "description": "ok",
                    "timestamp": at.isoformat()}],
        "problem_containers": [],
    }


def test_dashboard_periods_and_latest_snapshot(tmp_path, monkeypatch):
    monkeypatch.setenv("DASH_VPS_DATABASE_PATH", str(tmp_path / "dashboard.db"))
    monkeypatch.setenv("DASH_VPS_INGEST_TOKEN", "test-token")
    get_settings.cache_clear()
    end = datetime(2026, 10, 9, 12, tzinfo=timezone.utc)
    with TestClient(app) as client:
        assert client.get("/api/v1/dashboard").status_code == 404
        for days in (20, 3, 0):
            response = client.post("/api/v1/metrics", json=sample(end - timedelta(days=days), days),
                                   headers={"Authorization": "Bearer test-token"})
            assert response.status_code == 201
        for period, count in (("24h", 1), ("7d", 2), ("30d", 3)):
            response = client.get("/api/v1/dashboard", params={"period": period})
            assert response.status_code == 200
            report = response.json()
            assert report["version"] == 1
            assert report["hostname"] == "vps-test"
            assert report["host"] == {"cores": 4, "ramGb": 8, "diskGb": 80,
                                      "uptimeSeconds": 100, "os": "Linux", "region": "BR"}
            assert len(report["history"]) == count
            assert report["history"][-1]["cpu"] == 0
            assert len(report["alerts"]) == count
            assert report["services"][0]["latencyMs"] == 10
        assert client.get("/api/v1/dashboard", params={"period": "1y"}).status_code == 422
    get_settings.cache_clear()


def test_dashboard_history_is_bounded_and_deduplicated(tmp_path, monkeypatch):
    monkeypatch.setenv("DASH_VPS_DATABASE_PATH", str(tmp_path / "many.db"))
    monkeypatch.setenv("DASH_VPS_INGEST_TOKEN", "test-token")
    get_settings.cache_clear()
    end = datetime(2026, 10, 9, 12, tzinfo=timezone.utc)
    with TestClient(app) as client:
        for index in range(1002):
            response = client.post(
                "/api/v1/metrics", json=sample(end - timedelta(minutes=index)),
                headers={"Authorization": "Bearer test-token"},
            )
            assert response.status_code == 201
        assert len(client.get("/api/v1/dashboard").json()["history"]) == 1000
    get_settings.cache_clear()
