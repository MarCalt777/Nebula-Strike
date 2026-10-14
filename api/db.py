import sqlite3

DB_PATH = "game.db"

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    # Tabula rekodiem
    conn.execute("""
        CREATE TABLE IF NOT EXISTS scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player TEXT NOT NULL,
            score INTEGER NOT NULL
        )""")
    # Tabula spēlētājiem un parolēm (3. daļa)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS players (
            name TEXT PRIMARY KEY,
            password_hash TEXT NOT NULL,
            token TEXT
        )""")
    return conn