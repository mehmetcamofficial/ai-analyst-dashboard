import sqlite3
from datetime import datetime

conn = sqlite3.connect("saas.db", check_same_thread=False)
c = conn.cursor()

# USERS
c.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    created_at TEXT
)
""")

# USAGE LOGS
c.execute("""
CREATE TABLE IF NOT EXISTS usage (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    prompt TEXT,
    model TEXT,
    timestamp TEXT
)
""")

conn.commit()


def log_usage(username, prompt, model):
    c.execute(
        "INSERT INTO usage VALUES (NULL, ?, ?, ?, ?)",
        (username, prompt, model, datetime.now().isoformat())
    )
    conn.commit()
