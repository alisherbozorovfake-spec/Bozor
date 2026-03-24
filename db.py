import sqlite3

db = sqlite3.connect("database.db")
cursor = db.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    balance INTEGER DEFAULT 0
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS promos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    uc_amount TEXT,
    promo TEXT,
    status TEXT
)
""")

db.commit()

def get_balance(user_id):
    cursor.execute("SELECT balance FROM users WHERE user_id=?", (user_id,))
    res = cursor.fetchone()
    return res[0] if res else 0

def add_balance(user_id, amount):
    cursor.execute("UPDATE users SET balance = balance + ? WHERE user_id=?", (amount, user_id))
    db.commit()

def minus_balance(user_id, amount):
    cursor.execute("UPDATE users SET balance = balance - ? WHERE user_id=?", (amount, user_id))
    db.commit()
