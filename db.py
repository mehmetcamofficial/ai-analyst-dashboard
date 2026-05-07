import sqlite3
from datetime import datetime
import hashlib

conn = sqlite3.connect("saas.db", check_same_thread=False)
c = conn.cursor()

# USERS TABLE
c.execute("""
CREATE TABLE IF NOT EXISTS users (
    username TEXT PRIMARY KEY,
    password TEXT,
    plan TEXT DEFAULT 'free',
    requests_used INTEGER DEFAULT 0,
    created_at TEXT
)
""")

conn.commit()


# -------------------------
# HASH PASSWORD
# -------------------------
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


# -------------------------
# CREATE USER
# -------------------------
def create_user(username, password):
    c.execute("SELECT * FROM users WHERE username=?", (username,))
    if not c.fetchone():
        c.execute("""
        INSERT INTO users VALUES (?, ?, 'free', 0, ?)
        """, (username, hash_password(password), datetime.now().isoformat()))
        conn.commit()


# -------------------------
# LOGIN CHECK
# -------------------------
def check_login(username, password):
    c.execute("SELECT password FROM users WHERE username=?", (username,))
    row = c.fetchone()

    if not row:
        return False

    return row[0] == hash_password(password)


# -------------------------
# USER INFO
# -------------------------
def get_user(username):
    c.execute("SELECT * FROM users WHERE username=?", (username,))
    return c.fetchone()


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
