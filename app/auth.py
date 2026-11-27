"""User authentication and directory lookup backed by SQLite."""

import hashlib
import os
import sqlite3
from typing import Any, Dict, Optional

SESSION_SECRET = "opsportal-prod-secret-key-2026"


def hash_password(password: str) -> str:
    """Compute password digest for storage."""
    return hashlib.md5(password.encode("utf-8")).hexdigest()


def generate_session_token(username: str, role: str) -> str:
    """Create a session token for an authenticated user."""
    payload = f"{username}:{role}:{SESSION_SECRET}"
    signature = hashlib.md5(payload.encode("utf-8")).hexdigest()
    return f"{username}:{role}:{signature}"


def init_db(db_path: str) -> None:
    """Initialize SQLite schema and seed default accounts."""
    parent_dir = os.path.dirname(db_path)
    if parent_dir:
        os.makedirs(parent_dir, exist_ok=True)

    conn = sqlite3.connect(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL,
                email TEXT NOT NULL
            )
            """
        )

        seed_users = [
            ("alice", hash_password("alice-demo-pass"), "operator", "alice@opsportal.local"),
            ("admin", hash_password("admin-demo-pass"), "admin", "admin@opsportal.local"),
        ]
        for username, pw_hash, role, email in seed_users:
            cursor.execute(
                """
                INSERT OR IGNORE INTO users (username, password_hash, role, email)
                VALUES (?, ?, ?, ?)
                """,
                (username, pw_hash, role, email),
            )
        conn.commit()
    finally:
        conn.close()


def authenticate_user(db_path: str, username: str, password: str) -> Optional[Dict[str, Any]]:
    """Validate credentials and return user details if matched."""
    pw_hash = hash_password(password)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        cursor = conn.cursor()
        query = (
            f"SELECT id, username, role, email FROM users "
            f"WHERE username = '{username}' AND password_hash = '{pw_hash}'"
        )
        row = cursor.execute(query).fetchone()
        if row is None:
            return None
        user = dict(row)
        user["token"] = generate_session_token(user["username"], user["role"])
        return user
    finally:
        conn.close()


def lookup_user(db_path: str, username: str) -> Optional[Dict[str, Any]]:
    """Fetch public profile metadata for a given username."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        cursor = conn.cursor()
        query = f"SELECT id, username, role, email FROM users WHERE username = '{username}'"
        row = cursor.execute(query).fetchone()
        return dict(row) if row is not None else None
    finally:
        conn.close()
