import json
import sqlite3

import pytest
from fastapi.testclient import TestClient

from app.config import Settings, get_settings
from app.main import app


INGEST_TOKEN = "test-ingest-token"


@pytest.fixture
def client(tmp_path, monkeypatch):
    database_path = tmp_path / "metrics.db"
    monkeypatch.setenv("DASH_VPS_DATABASE_PATH", str(database_path))
    monkeypatch.setenv("DASH_VPS_INGEST_TOKEN", INGEST_TOKEN)
    get_settings.cache_clear()
    with TestClient(app) as test_client:
        yield test_client, database_path
    get_settings.cache_clear()


def payload(**overrides):
    snapshot = {
        "collected_at": "2026-10-09T12:00:00Z",
        "hostname": "vps-01",
        "cpu_percent": 24.8,
        "memory_percent": 62.4,
        "disk_percent": 56.6,
        "load_1m": 1.24,
        "uptime_seconds": 1977480,
        "containers": {"running": 12, "stopped": 1, "exited": 1, "restarting": 0},
        "services": [{"name": "Hermes", "online": True, "latency_ms": 42}],
        "alerts": [
            {
                "priority": "warning",
                "title": "Container encerrado",
                "timestamp": "2026-10-09T11:30:00Z",
            }
        ],
        "problem_containers": [
            {"name": "backup-worker", "state": "exited", "detail": "exit code 1"}
        ],
    }
    snapshot.update(overrides)
    return snapshot


def ingest(test_client, snapshot, authorization=f"Bearer {INGEST_TOKEN}"):
    headers = {"Authorization": authorization} if authorization is not None else {}
    return test_client.post("/api/v1/metrics", json=snapshot, headers=headers)


def test_ingest_metrics_returns_created_and_persists_snapshot(client):
    test_client, database_path = client

    response = ingest(test_client, payload())

    assert response.status_code == 201
    assert response.json() == {"id": 1, "collected_at": "2026-10-09T12:00:00Z"}
    with sqlite3.connect(database_path) as connection:
        row = connection.execute(
            "SELECT collected_at, hostname, cpu_percent, memory_percent, disk_percent, "
            "load_1m, uptime_seconds, containers_json, services_json, alerts_json, "
            "problem_containers_json "
            "FROM snapshots WHERE id = 1"
        ).fetchone()
    assert row[:7] == ("2026-10-09T12:00:00+00:00", "vps-01", 24.8, 62.4, 56.6, 1.24, 1977480)
    assert json.loads(row[7]) == {"running": 12, "stopped": 1, "exited": 1, "restarting": 0}
    assert json.loads(row[8]) == [{"name": "Hermes", "online": True, "latency_ms": 42.0}]
    assert json.loads(row[9]) == [
        {
            "priority": "warning",
            "title": "Container encerrado",
            "timestamp": "2026-10-09T11:30:00Z",
        }
    ]
    assert json.loads(row[10]) == [
        {"name": "backup-worker", "state": "exited", "detail": "exit code 1"}
    ]


@pytest.mark.parametrize(
    ("changes", "field"),
    [
        ({"cpu_percent": 100.1}, "cpu_percent"),
        ({"load_1m": -0.1}, "load_1m"),
        ({"uptime_seconds": -1}, "uptime_seconds"),
        ({"containers": {"running": 1.5, "stopped": 0, "exited": 0, "restarting": 0}}, "running"),
        ({"collected_at": "not-a-date"}, "collected_at"),
        ({"collected_at": "2026-10-09T12:00:00"}, "collected_at"),
    ],
)
def test_ingest_metrics_rejects_invalid_payloads(client, changes, field):
    test_client, _ = client

    response = ingest(test_client, payload(**changes))

    assert response.status_code == 422
    assert any(field in str(error["loc"]) for error in response.json()["detail"])


def test_ingest_metrics_accepts_omitted_optional_structures(client):
    test_client, database_path = client

    snapshot = payload()
    snapshot.pop("services")
    snapshot.pop("alerts")
    snapshot.pop("problem_containers")
    response = ingest(test_client, snapshot)

    assert response.status_code == 201
    with sqlite3.connect(database_path) as connection:
        optional_values = connection.execute(
            "SELECT services_json, alerts_json, problem_containers_json "
            "FROM snapshots WHERE id = 1"
        ).fetchone()
    assert optional_values == (None, None, None)


def test_ingest_metrics_stores_multiple_snapshots(client):
    test_client, database_path = client

    first = ingest(test_client, payload())
    second = ingest(test_client, payload(collected_at="2026-10-09T12:05:00Z", cpu_percent=25))

    assert first.json()["id"] == 1
    assert second.status_code == 201
    assert second.json()["id"] == 2
    with sqlite3.connect(database_path) as connection:
        count = connection.execute("SELECT COUNT(*) FROM snapshots").fetchone()[0]
    assert count == 2


def test_ingest_metrics_rejects_missing_authorization(client):
    test_client, database_path = client

    response = ingest(test_client, payload(), authorization=None)

    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"
    with sqlite3.connect(database_path) as connection:
        count = connection.execute("SELECT COUNT(*) FROM snapshots").fetchone()[0]
    assert count == 0


def test_ingest_metrics_rejects_invalid_token(client):
    test_client, _ = client

    response = ingest(test_client, payload(), authorization="Bearer wrong-token")

    assert response.status_code == 401


@pytest.mark.parametrize(
    "authorization",
    ["test-ingest-token", "Basic test-ingest-token", "Bearer", "Bearer ", "Bearer token extra"],
)
def test_ingest_metrics_rejects_malformed_authorization(client, authorization):
    test_client, _ = client

    response = ingest(test_client, payload(), authorization=authorization)

    assert response.status_code == 401


def test_ingest_metrics_fails_closed_without_configured_token(client):
    test_client, database_path = client
    app.dependency_overrides[get_settings] = lambda: Settings(
        database_path=database_path, ingest_token=None
    )
    try:
        response = ingest(test_client, payload())
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 503
    assert response.json() == {"detail": "Metrics ingestion is not configured"}
