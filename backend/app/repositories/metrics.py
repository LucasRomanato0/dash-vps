import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

from app.database import get_connection
from app.schemas.metrics import MetricsSnapshotCreate


def create_snapshot(database_path: Path, snapshot: MetricsSnapshotCreate) -> int:
    """Store a snapshot atomically, keeping nested portions as JSON text."""
    values = {
        "collected_at": snapshot.collected_at.isoformat(),
        "hostname": snapshot.hostname,
        "cores": snapshot.cores,
        "ram_gb": snapshot.ram_gb,
        "disk_gb": snapshot.disk_gb,
        "os": snapshot.os,
        "region": snapshot.region,
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
    # Columns are fixed by this module, never supplied by a request.
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
    return None if value is None else json.dumps([item.model_dump(mode="json", exclude_unset=True) for item in value])


PERIOD_DAYS = {"24h": 1, "7d": 7, "30d": 30}
MAX_HISTORY = 1000


def get_dashboard(database_path: Path, period: str) -> dict | None:
    """Read the latest snapshot and at most 1000 samples within the selected period."""
    with get_connection(database_path) as connection:
        latest = connection.execute(
            "SELECT * FROM snapshots ORDER BY collected_at DESC, id DESC LIMIT 1"
        ).fetchone()
        if latest is None:
            return None
        end = _parse_timestamp(latest["collected_at"])
        start = end - timedelta(days=PERIOD_DAYS[period])
        rows = connection.execute(
            "SELECT collected_at, cpu_percent, memory_percent, disk_percent, "
            "load_1m, containers_json, alerts_json FROM snapshots "
            "WHERE datetime(collected_at) BETWEEN datetime(?) AND datetime(?) "
            "ORDER BY collected_at DESC, id DESC LIMIT ?",
            (start.isoformat(), latest["collected_at"], MAX_HISTORY),
        ).fetchall()

    # A repeated timestamp can occur when a collector retries; keep its newest row.
    points = []
    alerts = {}
    seen = set()
    for row in rows:
        timestamp = row["collected_at"]
        if timestamp not in seen and all(row[key] is not None for key in (
            "cpu_percent", "memory_percent", "disk_percent", "load_1m", "containers_json"
        )):
            seen.add(timestamp)
            points.append({
                "timestamp": timestamp, "cpu": row["cpu_percent"],
                "ram": row["memory_percent"], "disk": row["disk_percent"],
                "load": row["load_1m"], "containers": json.loads(row["containers_json"]),
            })
        for alert in json.loads(row["alerts_json"] or "[]"):
            alert_at = _parse_timestamp(alert["timestamp"])
            if start <= alert_at <= end:
                alerts[(alert_at, alert["title"])] = alert
    points.reverse()
    return {
        "version": 1,
        "hostname": latest["hostname"] or "unknown",
        "collectedAt": latest["collected_at"],
        "host": {
            "cores": latest["cores"] or 1,
            "ramGb": latest["ram_gb"] or 0,
            "diskGb": latest["disk_gb"] or 0,
            "uptimeSeconds": latest["uptime_seconds"] or 0,
            "os": latest["os"] or "",
            "region": latest["region"] or "",
        },
        "history": points,
        "services": [
            {"name": s["name"], "description": s.get("description", ""),
             "online": s["online"], "latencyMs": s.get("latency_ms")}
            for s in json.loads(latest["services_json"] or "[]")
        ],
        "alerts": sorted(alerts.values(), key=lambda a: _parse_timestamp(a["timestamp"]), reverse=True)[:100],
        "problemContainers": json.loads(latest["problem_containers_json"] or "[]"),
    }


def _parse_timestamp(value: str) -> datetime:
    """Normalize legacy SQLite timestamps before using them in period math."""
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)
