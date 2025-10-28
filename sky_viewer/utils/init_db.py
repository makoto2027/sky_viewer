import sqlite3
import os

# 保存先のパス
DB_PATH = os.path.join("database", "history.db")

def init_db():
    os.makedirs("database", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # テーブル作成
    cur.execute("""
    CREATE TABLE IF NOT EXISTS history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        city TEXT NOT NULL,
        weather TEXT,
        temperature TEXT,
        humidity TEXT,
        icon TEXT,
        method TEXT,
        search_time TEXT,
        favorite INTEGER DEFAULT 0
    )
    """)

    conn.commit()
    conn.close()
    print("✅ データベース初期化完了：history.db")

if __name__ == "__main__":
    init_db()
