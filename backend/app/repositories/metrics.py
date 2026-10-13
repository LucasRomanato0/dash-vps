import json
from pathlib import Path

from app.database import get_connection
from app.schemas.metrics import MetricsSnapshotCreate


def create_snapshot(database_path: Path, snapshot: MetricsSnapshotCreate) -> int:
    """Store a snapshot atomically, keeping nested portions as JSON text."""
    values = {
        "collected_at": snapshot.collected_at.isoformat(),
        "hostname": snapshot.hostname,
        "cpu_percent": snapshot.cpu_percent,
        "memory_percent": snapshot.memory_percent,
        "disk_percent": snapshot.disk_percent,
        "load_1m": snapshot.load_1m,
        "uptime_seconds": snapshot.uptime_seconds,
        "containers_json": json.dumps(snapshot.containers.model_dump()),
        "services_json": _dump_optional(snapshot.services),
        "alerts_json": _dump_optional(snapshot.alerts),
        "problem_containers_json": _dump_optional(snapshot.problem_containers),
    }
    columns = ", ".join(values)
    placeholders = ", ".join(f":{column}" for column in values)
    query = f"INSERT INTO snapshots ({columns}) VALUES ({placeholders})"

    # The connection context commits on success and rolls back on exceptions.
    with get_connection(database_path) as connection:
        cursor = connection.execute(query, values)
        snapshot_id = cursor.lastrowid

    if snapshot_id is None:
        raise RuntimeError("SQLite did not return a snapshot id")
    return int(snapshot_id)


def _dump_optional(value: object | None) -> str | None:
    return None if value is None else json.dumps(value)
