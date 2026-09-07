"""
Проста SQLite база, щоб не надсилати одне й те саме нагадування двічі
(наприклад, якщо бот перезапуститься посеред дня).
"""
import sqlite3
from contextlib import contextmanager

DB_PATH = "bot.db"


def init_db():
    with _connect() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS sent_reminders (
                match_id INTEGER NOT NULL,
                reminder_type TEXT NOT NULL,  -- 'morning' або 'hour_before'
                PRIMARY KEY (match_id, reminder_type)
            )
        """)


@contextmanager
def _connect():
    conn = sqlite3.connect(DB_PATH)
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def was_sent(match_id: int, reminder_type: str) -> bool:
    with _connect() as conn:
        cur = conn.execute(
            "SELECT 1 FROM sent_reminders WHERE match_id = ? AND reminder_type = ?",
            (match_id, reminder_type),
        )
        return cur.fetchone() is not None


def mark_sent(match_id: int, reminder_type: str):
    with _connect() as conn:
        conn.execute(
            "INSERT OR IGNORE INTO sent_reminders (match_id, reminder_type) VALUES (?, ?)",
            (match_id, reminder_type),
        )
