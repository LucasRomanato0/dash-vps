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
    }
