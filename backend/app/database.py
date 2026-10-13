import sqlite3
from pathlib import Path


SNAPSHOTS_SCHEMA = """
CREATE TABLE IF NOT EXISTS snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    collected_at TEXT NOT NULL,
    hostname TEXT,
    cores INTEGER,
    ram_gb REAL,
    disk_gb REAL,
    os TEXT,
    region TEXT,
    cpu_percent REAL,
    memory_percent REAL,
    disk_percent REAL,
    load_1m REAL,
    uptime_seconds INTEGER,
    containers_json TEXT,
    services_json TEXT,
    alerts_json TEXT,
    problem_containers_json TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
)
"""

# Kept separately so installations created by the first backend increment can
# be upgraded in place without losing their existing snapshots.
SNAPSHOT_COLUMNS = {
    "cpu_percent": "REAL",
    "memory_percent": "REAL",
    "disk_percent": "REAL",
    "hostname": "TEXT",
    "cores": "INTEGER",
    "ram_gb": "REAL",
    "disk_gb": "REAL",
    "os": "TEXT",
    "region": "TEXT",
    "load_1m": "REAL",
    "uptime_seconds": "INTEGER",
    "containers_json": "TEXT",
    "services_json": "TEXT",
    "alerts_json": "TEXT",
    "problem_containers_json": "TEXT",
}

# This is deliberately a module-owned, fixed list.  SQLite identifiers cannot
# be bound as parameters, so migrations must never interpolate caller input.


def get_connection(database_path: Path) -> sqlite3.Connection:
    """Open a SQLite connection, creating its parent directory when needed."""
    database_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(database_path, timeout=10)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA busy_timeout = 10000")
    return connection


def initialize_database(database_path: Path) -> None:
    """Apply the snapshots schema and compatible additive migrations."""
    with get_connection(database_path) as connection:
        connection.execute(SNAPSHOTS_SCHEMA)
        existing_columns = {
            row["name"] for row in connection.execute("PRAGMA table_info(snapshots)")
        }
        for column, definition in SNAPSHOT_COLUMNS.items():
            if column not in existing_columns:
                connection.execute(
                    f"ALTER TABLE snapshots ADD COLUMN {column} {definition}"
                )
        connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_snapshots_collected_at "
            "ON snapshots (collected_at DESC, id DESC)"
        )
