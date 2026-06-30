import sqlite3
import threading
from pathlib import Path
from contextlib import contextmanager
from typing import Iterator

from app.core.config import settings


_local = threading.local()


def get_connection() -> sqlite3.Connection:
    if not hasattr(_local, "conn") or _local.conn is None:
        db_path = settings.database_dir / "invoices.db"
        _local.conn = sqlite3.connect(str(db_path), check_same_thread=False)
        _local.conn.row_factory = sqlite3.Row
        _local.conn.execute("PRAGMA journal_mode=WAL")
        _local.conn.execute("PRAGMA foreign_keys=ON")
    return _local.conn


@contextmanager
def get_db() -> Iterator[sqlite3.Connection]:
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise


def init_db():
    conn = get_connection()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS invoices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            file_path TEXT,
            original_text TEXT,
            structured_json TEXT,
            processing_time_ms REAL,
            cpu_usage REAL,
            memory_usage REAL,
            model_used TEXT,
            status TEXT DEFAULT 'pending',
            error_message TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE INDEX IF NOT EXISTS idx_invoices_status ON invoices(status);
        CREATE INDEX IF NOT EXISTS idx_invoices_created_at ON invoices(created_at);
        CREATE INDEX IF NOT EXISTS idx_invoices_filename ON invoices(filename);

        CREATE TABLE IF NOT EXISTS processing_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_id INTEGER REFERENCES invoices(id) ON DELETE CASCADE,
            stage TEXT NOT NULL,
            message TEXT,
            duration_ms REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    try:
        conn.execute("ALTER TABLE invoices ADD COLUMN file_path TEXT")
    except sqlite3.OperationalError:
        pass

    conn.commit()


def cleanup_connection():
    if hasattr(_local, "conn") and _local.conn is not None:
        _local.conn.close()
        _local.conn = None
