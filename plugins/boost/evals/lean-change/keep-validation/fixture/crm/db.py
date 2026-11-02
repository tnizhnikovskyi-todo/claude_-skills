"""Тонкая обёртка над sqlite3, используется во всём проекте."""
import sqlite3
from contextlib import contextmanager


@contextmanager
def transaction(path="crm.db"):
    conn = sqlite3.connect(path)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
