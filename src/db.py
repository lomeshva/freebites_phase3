import sqlite3
from pathlib import Path

# Path to instance/freebites.db relative to this file
BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "instance" / "freebites.db"
SQL_DIR = BASE_DIR / "sql"


def get_conn():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create all tables and seed sample data."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with get_conn() as conn:
        with open(SQL_DIR / "init_db.sql", "r", encoding="utf-8") as f:
            conn.executescript(f.read())
        conn.commit()
