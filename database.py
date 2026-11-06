import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "agent_memory.db"

def get_connection():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection

def initialize_database():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                description TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS conversation_memory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)

def save_message(role: str, content: str):
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO conversation_memory (role, content) VALUES (?, ?)",
            (role, content)
        )

def load_recent_messages(limit: int = 12):
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT role, content FROM conversation_memory ORDER BY id DESC LIMIT ?",
            (limit,)
        ).fetchall()
    return [dict(row) for row in reversed(rows)]

def clear_conversation_memory():
    with get_connection() as conn:
        conn.execute("DELETE FROM conversation_memory")
