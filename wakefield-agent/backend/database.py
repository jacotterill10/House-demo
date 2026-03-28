import sqlite3

DB_PATH = "backend/properties.db"

def get_connection():
    return sqlite3.connect(DB_PATH)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS listings (
        id INTEGER PRIMARY KEY,
        title TEXT NOT NULL,
        price INTEGER NOT NULL,
        area TEXT NOT NULL,
        beds INTEGER NOT NULL,
        baths INTEGER NOT NULL,
        type TEXT NOT NULL,
        commute INTEGER NOT NULL,
        size INTEGER NOT NULL,
        lat REAL NOT NULL,
        lng REAL NOT NULL,
        url TEXT NOT NULL
    )
    """)

    conn.commit()
    conn.close()