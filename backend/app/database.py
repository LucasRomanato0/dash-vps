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


def get_connection(database_path: Path) -> sqlite3.Connection:
    """Open a SQLite connection, creating its parent directory when needed."""
    database_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(database_path)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database(database_path: Path) -> None:
    """Apply the small bootstrap schema; safe to run on every startup."""
    with get_connection(database_path) as connection:
        connection.execute(SNAPSHOTS_SCHEMA)
