
import hashlib
import hmac
import os
import secrets
import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "jobpilot_users.db"

def _connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_auth_db():
    with _connect() as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'user'
        )""")
        cols = [r['name'] for r in conn.execute("PRAGMA table_info(users)").fetchall()]
        if 'role' not in cols:
            conn.execute("ALTER TABLE users ADD COLUMN role TEXT NOT NULL DEFAULT 'user'")
        conn.commit()

def _hash_password(password):
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 200000)
    return salt.hex() + ":" + digest.hex()

def _verify_password(password, stored):
    try:
        salt_hex, digest_hex = stored.split(":", 1)
        salt = bytes.fromhex(salt_hex)
        expected = bytes.fromhex(digest_hex)
        actual = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 200000)
        return hmac.compare_digest(actual, expected)
    except Exception:
        return False

def register_user(name, email, password):
    email = email.strip().lower()
    if not name.strip() or not email or len(password) < 8:
        return False, "Enter a name, valid email and password of at least 8 characters."
    try:
        with _connect() as conn:
            conn.execute(
                "INSERT INTO users(name,email,password_hash,created_at) VALUES(?,?,?,?)",
                (name.strip(), email, _hash_password(password), datetime.utcnow().isoformat())
            )
            conn.commit()
        return True, "Account created. Please log in."
    except sqlite3.IntegrityError:
        return False, "An account with this email already exists."

def login_user(email, password):
    with _connect() as conn:
        row = conn.execute("SELECT * FROM users WHERE email=?", (email.strip().lower(),)).fetchone()
    if row and _verify_password(password, row["password_hash"]):
        return dict(row)
    return None


def list_users():
    with _connect() as conn:
        rows = conn.execute("SELECT id,name,email,created_at,role FROM users ORDER BY created_at DESC").fetchall()
    return [dict(r) for r in rows]

def set_user_role(user_id, role):
    if role not in ("user", "admin"):
        return False
    with _connect() as conn:
        conn.execute("UPDATE users SET role=? WHERE id=?", (role, user_id))
        conn.commit()
    return True
