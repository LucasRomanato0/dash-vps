import sqlite3
from pathlib import Path


SNAPSHOTS_SCHEMA = """
CREATE TABLE IF NOT EXISTS snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    collected_at TEXT NOT NULL,
    cpu_percent REAL,
    memory_percent REAL,
    disk_percent REAL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
)
"""

# Kept separately so installations created by the first backend increment can
# be upgraded in place without losing their existing snapshots.
SNAPSHOT_COLUMNS = {
    "hostname": "TEXT",
    "load_1m": "REAL",
    "uptime_seconds": "INTEGER",
    "containers_json": "TEXT",
    "services_json": "TEXT",
    "alerts_json": "TEXT",
    "problem_containers_json": "TEXT",
}


def get_connection(database_path: Path) -> sqlite3.Connection:
    """Open a SQLite connection, creating its parent directory when needed."""
    database_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(database_path)
    connection.row_factory = sqlite3.Row
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
