import sqlite3

def get_connection():
    conn = sqlite3.connect("game.db")
    return conn

def init_db():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS players (
                name TEXT PRIMARY KEY,
                password_hash TEXT,
                token TEXT
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS scores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player TEXT,
                score INTEGER
            )
        """)

if __name__ == "__main__":
    init_db()