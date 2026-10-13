import sqlite3

from app.database import initialize_database


def test_initialize_database_creates_file_and_snapshots_table(tmp_path):
    database_path = tmp_path / "nested" / "test.db"

    initialize_database(database_path)

    assert database_path.is_file()
    with sqlite3.connect(database_path) as connection:
        tables = connection.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table' AND name = 'snapshots'"
        ).fetchall()
        columns = connection.execute("PRAGMA table_info(snapshots)").fetchall()

    assert tables == [("snapshots",)]
    assert {column[1] for column in columns} >= {
        "id",
        "collected_at",
        "cpu_percent",
        "memory_percent",
        "disk_percent",
        "created_at",
        "hostname",
        "load_1m",
        "uptime_seconds",
        "containers_json",
        "services_json",
        "alerts_json",
        "problem_containers_json",
    }


def test_initialize_database_upgrades_initial_schema_idempotently(tmp_path):
    database_path = tmp_path / "legacy.db"
    with sqlite3.connect(database_path) as connection:
        connection.execute(
            "CREATE TABLE snapshots (id INTEGER PRIMARY KEY, collected_at TEXT NOT NULL, "
            "cpu_percent REAL, memory_percent REAL, disk_percent REAL, created_at TEXT)"
        )

    initialize_database(database_path)
    initialize_database(database_path)

    with sqlite3.connect(database_path) as connection:
        columns = {column[1] for column in connection.execute("PRAGMA table_info(snapshots)")}
    assert {
        "hostname",
        "load_1m",
        "uptime_seconds",
        "containers_json",
        "services_json",
        "alerts_json",
        "problem_containers_json",
    } <= columns
