import sqlite3
import os
from datetime import datetime
import hashlib

DB_NAME = "saas.db"

# 🔥 AUTO RESET FIX (CRITICAL)
if os.path.exists(DB_NAME):
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
else:
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)

c = conn.cursor()

# =========================
# FORCE SAFE TABLE CREATE
# =========================

c.execute("DROP TABLE IF EXISTS users")

c.execute("""
CREATE TABLE users (
    username TEXT PRIMARY KEY,
    password TEXT,
    plan TEXT,
    requests_used INTEGER,
    created_at TEXT
)
""")

conn.commit()

# =========================
# HASH
# =========================

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# =========================
# CREATE USER (FIXED)
# =========================

def create_user(username, password):

    c.execute("SELECT username FROM users WHERE username=?", (username,))
    if not c.fetchone():

        c.execute("""
        INSERT INTO users VALUES (?, ?, 'free', 0, ?)
        """, (
            username,
            hash_password(password),
            datetime.now().isoformat()
        ))

        conn.commit()

# =========================
# LOGIN
# =========================

def check_login(username, password):

    c.execute("SELECT password FROM users WHERE username=?", (username,))
    row = c.fetchone()

    if not row:
        return False

    return row[0] == hash_password(password)

# =========================
# GET USER
# =========================

def get_user(username):
    c.execute("SELECT * FROM users WHERE username=?", (username,))
    return c.fetchone()

# =========================
# USAGE
# =========================

def increment_usage(username):
    c.execute("""
    UPDATE users
    SET requests_used = requests_used + 1
    WHERE username=?
    """, (username,))
    conn.commit()

# =========================
# PLAN
# =========================

def set_plan(username, plan):
    c.execute("""
    UPDATE users SET plan=? WHERE username=?
    """, (plan, username))
    conn.commit()
