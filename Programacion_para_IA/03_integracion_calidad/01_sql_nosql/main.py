"""Create the SQLite example and read a parameterized query into pandas."""

import sqlite3
from contextlib import closing
from pathlib import Path

import pandas as pd

from sample_data import DOCUMENTS

DB_PATH = Path(__file__).resolve().parent / "outputs" / "documents.db"


def prepare_database(path: Path) -> None:
    """Restore the six example documents in this session's generated database."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with closing(sqlite3.connect(path, autocommit=False)) as connection:
        with connection:
            connection.execute("""
                CREATE TABLE IF NOT EXISTS documents (
                    id INTEGER PRIMARY KEY,
                    title TEXT NOT NULL,
                    topic TEXT NOT NULL,
                    pages INTEGER NOT NULL CHECK (pages > 0)
                )
            """)
            connection.execute("DELETE FROM documents")
            connection.executemany(
                "INSERT INTO documents (id, title, topic, pages) VALUES (?, ?, ?, ?)",
                DOCUMENTS,
            )


def main() -> None:
    prepare_database(DB_PATH)
    with closing(sqlite3.connect(DB_PATH, autocommit=False)) as connection:
        documents = pd.read_sql_query(
            "SELECT title, pages FROM documents WHERE topic = ? ORDER BY id",
            connection,
            params=("retrieval",),
        )
    print(documents.to_string(index=False))
    print("Database:", DB_PATH)


if __name__ == "__main__":
    main()
