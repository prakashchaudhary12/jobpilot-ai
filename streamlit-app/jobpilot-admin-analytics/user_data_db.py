# SECURITY: user-owned records must be filtered by authenticated user_id.

import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).resolve().parent / "jobpilot_users.db"

def _connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_user_data_db():
    with _connect() as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS user_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            item_type TEXT NOT NULL,
            title TEXT NOT NULL,
            content TEXT DEFAULT '',
            created_at TEXT NOT NULL
        )""")
        conn.commit()

def save_user_item(user_id, item_type, title, content=""):
    with _connect() as conn:
        conn.execute(
            "INSERT INTO user_items(user_id,item_type,title,content,created_at) VALUES(?,?,?,?,?)",
            (int(user_id), item_type, title, content, datetime.utcnow().isoformat())
        )
        conn.commit()

def get_user_items(user_id, item_type=None):
    with _connect() as conn:
        if item_type:
            rows = conn.execute(
                "SELECT * FROM user_items WHERE user_id=? AND item_type=? ORDER BY id DESC",
                (int(user_id), item_type)
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM user_items WHERE user_id=? ORDER BY id DESC",
                (int(user_id),)
            ).fetchall()
    return [dict(row) for row in rows]
