import sqlite3
import datetime
import random
import string
import logging

logger = logging.getLogger(__name__)

DB_NAME = "neuroflux.db"

def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    c.executescript("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        telegram_id INTEGER UNIQUE NOT NULL,
        username TEXT,
        first_name TEXT,
        last_name TEXT,
        referral_code TEXT UNIQUE,
        referred_by INTEGER,
        referral_count INTEGER DEFAULT 0,
        plan TEXT DEFAULT 'free',
        daily_bonus_claimed_at TEXT,
        ai_messages_today INTEGER DEFAULT 0,
        ai_messages_date TEXT,
        total_points INTEGER DEFAULT 0,
        unlocked INTEGER DEFAULT 0,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        last_active TEXT DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS notes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        note_text TEXT NOT NULL,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS habits (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        habit_name TEXT NOT NULL,
        streak INTEGER DEFAULT 0,
        last_checked TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS finance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        type TEXT NOT NULL,
        amount REAL NOT NULL,
        description TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS chat_memory (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        role TEXT NOT NULL,
        content TEXT NOT NULL,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS score_results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        occupation TEXT,
        monthly_income TEXT,
        target_income TEXT,
        score INTEGER,
        insight TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    """)
    conn.commit()
    conn.close()
    logger.info("Database initialized.")

def register_user(telegram_id, username, first_name, last_name, referred_by=None):
    conn = get_db()
    c = conn.cursor()
    try:
        ref_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        c.execute(
            "INSERT INTO users (telegram_id, username, first_name, last_name, referral_code, referred_by) VALUES (?, ?, ?, ?, ?, ?)",
            (telegram_id, username, first_name, last_name, ref_code, referred_by)
        )
        conn.commit()
        if referred_by:
            c.execute("UPDATE users SET referral_count = referral_count + 1 WHERE telegram_id = ?", (referred_by,))
            c.execute("UPDATE users SET total_points = total_points + 10 WHERE telegram_id = ?", (referred_by,))
            # Auto-unlock if 3+ referrals
            c.execute("UPDATE users SET unlocked = 1 WHERE telegram_id = ? AND referral_count >= 3", (referred_by,))
            conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def get_user(telegram_id):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE telegram_id = ?", (telegram_id,))
    user = c.fetchone()
    conn.close()
    return user

def update_last_active(telegram_id):
    conn = get_db()
    c = conn.cursor()
    c.execute("UPDATE users SET last_active = ? WHERE telegram_id = ?", (datetime.datetime.now().isoformat(), telegram_id))
    conn.commit()
    conn.close()

def get_all_user_ids():
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT telegram_id FROM users")
    ids = [row["telegram_id"] for row in c.fetchall()]
    conn.close()
    return ids

def get_user_count():
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) as cnt FROM users")
    cnt = c.fetchone()["cnt"]
    conn.close()
    return cnt

def get_paid_user_count():
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) as cnt FROM users WHERE plan != 'free'")
    cnt = c.fetchone()["cnt"]
    conn.close()
    return cnt

def check_ai_limit(telegram_id):
    conn = get_db()
    c = conn.cursor()
    today = datetime.date.today().isoformat()
    c.execute("SELECT ai_messages_today, ai_messages_date, plan FROM users WHERE telegram_id = ?", (telegram_id,))
    row = c.fetchone()
    conn.close()
    if not row:
        return False, 0
    if row["plan"] != "free":
        return True, 999
    if row["ai_messages_date"] != today:
        return True, 5
    remaining = 5 - row["ai_messages_today"]
    return remaining > 0, remaining

def increment_ai_usage(telegram_id):
    conn = get_db()
    c = conn.cursor()
    today = datetime.date.today().isoformat()
    c.execute("SELECT ai_messages_date FROM users WHERE telegram_id = ?", (telegram_id,))
    row = c.fetchone()
    if row and row["ai_messages_date"] == today:
        c.execute("UPDATE users SET ai_messages_today = ai_messages_today + 1 WHERE telegram_id = ?", (telegram_id,))
    else:
        c.execute("UPDATE users SET ai_messages_today = 1, ai_messages_date = ? WHERE telegram_id = ?", (today, telegram_id))
    conn.commit()
    conn.close()

def is_unlocked(telegram_id):
    user = get_user(telegram_id)
    if not user:
        return False
    return user["unlocked"] == 1 or user["plan"] != "free"

def get_referral_code(telegram_id):
    user = get_user(telegram_id)
    return user["referral_code"] if user else None

def find_user_by_referral_code(code):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT telegram_id FROM users WHERE referral_code = ?", (code,))
    row = c.fetchone()
    conn.close()
    return row["telegram_id"] if row else None

# Notes
def add_note(user_id, text):
    conn = get_db()
    c = conn.cursor()
    c.execute("INSERT INTO notes (user_id, note_text) VALUES (?, ?)", (user_id, text))
    conn.commit()
    conn.close()

def get_notes(user_id):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT note_text, created_at FROM notes WHERE user_id = ? ORDER BY id DESC LIMIT 20", (user_id,))
    notes = c.fetchall()
    conn.close()
    return notes

# Habits
def add_habit(user_id, name):
    conn = get_db()
    c = conn.cursor()
    c.execute("INSERT INTO habits (user_id, habit_name) VALUES (?, ?)", (user_id, name))
    conn.commit()
    conn.close()

def get_habits(user_id):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM habits WHERE user_id = ?", (user_id,))
    habits = c.fetchall()
    conn.close()
    return habits

def check_habit(habit_id):
    conn = get_db()
    c = conn.cursor()
    today = datetime.date.today().isoformat()
    c.execute("SELECT last_checked, streak FROM habits WHERE id = ?", (habit_id,))
    row = c.fetchone()
    if row:
        if row["last_checked"] == today:
            conn.close()
            return False, row["streak"]
        yesterday = (datetime.date.today() - datetime.timedelta(days=1)).isoformat()
        new_streak = row["streak"] + 1 if row["last_checked"] == yesterday else 1
        c.execute("UPDATE habits SET streak = ?, last_checked = ? WHERE id = ?", (new_streak, today, habit_id))
        conn.commit()
        conn.close()
        return True, new_streak
    conn.close()
    return False, 0

# Finance
def add_finance(user_id, type_, amount, desc):
    conn = get_db()
    c = conn.cursor()
    c.execute("INSERT INTO finance (user_id, type, amount, description) VALUES (?, ?, ?, ?)", (user_id, type_, amount, desc))
    conn.commit()
    conn.close()

def get_finance_summary(user_id):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT COALESCE(SUM(CASE WHEN type='income' THEN amount ELSE 0 END), 0) as total_income, COALESCE(SUM(CASE WHEN type='expense' THEN amount ELSE 0 END), 0) as total_expense FROM finance WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    conn.close()
    return row["total_income"], row["total_expense"]

# Chat Memory
def save_chat_message(user_id, role, content):
    conn = get_db()
    c = conn.cursor()
    c.execute("INSERT INTO chat_memory (user_id, role, content) VALUES (?, ?, ?)", (user_id, role, content))
    conn.commit()
    conn.close()

def get_chat_history(user_id, limit=10):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT role, content FROM chat_memory WHERE user_id = ? ORDER BY id DESC LIMIT ?", (user_id, limit))
    rows = c.fetchall()
    conn.close()
    return list(reversed([{"role": r["role"], "content": r["content"]} for r in rows]))

def clear_chat_history(user_id):
    conn = get_db()
    c = conn.cursor()
    c.execute("DELETE FROM chat_memory WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

# Score results
def save_score(user_id, occupation, monthly, target, score, insight):
    conn = get_db()
    c = conn.cursor()
    c.execute("INSERT INTO score_results (user_id, occupation, monthly_income, target_income, score, insight) VALUES (?, ?, ?, ?, ?, ?)",
              (user_id, occupation, monthly, target, score, insight))
    conn.commit()
    conn.close()

# Daily bonus
def claim_daily_bonus(telegram_id):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT daily_bonus_claimed_at FROM users WHERE telegram_id = ?", (telegram_id,))
    row = c.fetchone()
    if row:
        last = row["daily_bonus_claimed_at"]
        if last:
            last_dt = datetime.datetime.fromisoformat(last)
            if (datetime.datetime.now() - last_dt).total_seconds() < 86400:
                conn.close()
                return False, 0
    now = datetime.datetime.now().isoformat()
    c.execute("UPDATE users SET daily_bonus_claimed_at = ?, total_points = total_points + 5 WHERE telegram_id = ?", (now, telegram_id))
    conn.commit()
    c.execute("SELECT total_points FROM users WHERE telegram_id = ?", (telegram_id,))
    pts = c.fetchone()["total_points"]
    conn.close()
    return True, pts
