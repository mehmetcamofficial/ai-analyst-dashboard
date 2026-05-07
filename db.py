import sqlite3
from datetime import datetime

conn = sqlite3.connect("saas.db", check_same_thread=False)
c = conn.cursor()

# USERS
c.execute("""
CREATE TABLE IF NOT EXISTS users (
    username TEXT PRIMARY KEY,
    plan TEXT DEFAULT 'free',
    requests_used INTEGER DEFAULT 0,
    created_at TEXT
)
""")

# LOGS
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


def get_user(username):
    c.execute("SELECT * FROM users WHERE username=?", (username,))
    return c.fetchone()


def create_user(username):
    c.execute("""
    INSERT OR IGNORE INTO users VALUES (?, 'free', 0, ?)
    """, (username, datetime.now().isoformat()))
    conn.commit()


def increment_usage(username):
    c.execute("""
    UPDATE users
    SET requests_used = requests_used + 1
    WHERE username=?
    """, (username,))
    conn.commit()


def set_plan(username, plan):
    c.execute("""
    UPDATE users SET plan=? WHERE username=?
    """, (plan, username))
    conn.commit()
