import sqlite3
from .config import DB_PATH

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS sticker_sets (
                set_name TEXT PRIMARY KEY,
                title TEXT
            )
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS user_sets (
                user_id INTEGER,
                set_name TEXT,
                PRIMARY KEY(user_id, set_name)
            )
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS stickers (
                file_id TEXT PRIMARY KEY,
                set_name TEXT,
                emoji TEXT,
                text TEXT
            )
        ''')