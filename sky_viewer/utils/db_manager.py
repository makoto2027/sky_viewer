import sqlite3
import os
from datetime import datetime, timedelta

DB_PATH = os.path.join("database", "history.db")

def get_connection():
    return sqlite3.connect(DB_PATH)

# ① 履歴の追加
def add_history(data):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO history (city, weather, temperature, humidity, icon, method, search_time, favorite)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data["city"],
        data.get("weather"),
        data.get("temperature"),
        data.get("humidity"),
        data.get("icon"),
        data.get("method"),
        data.get("search_time"),
        data.get("favorite", 0)
    ))
    conn.commit()
    conn.close()

# ② 履歴の取得（お気に入り or 最近N日以内）
def get_history(only_favorites=False, days_limit=7, order_by="search_time DESC"):
    conn = get_connection()
    cur = conn.cursor()

    # フィルター条件構築
    query = "SELECT * FROM history WHERE 1=1"
    params = []

    # 日数制限
    if days_limit:
        threshold = (datetime.now() - timedelta(days=days_limit)).strftime("%Y-%m-%d %H:%M:%S")
        query += " AND search_time >= ?"
        params.append(threshold)

    # お気に入りフィルタ
    if only_favorites:
        query += " AND favorite = 1"

    # 並び替え
    query += f" ORDER BY {order_by}"

    cur.execute(query, params)
    rows = cur.fetchall()
    columns = [col[0] for col in cur.description]
    conn.close()

    return [dict(zip(columns, row)) for row in rows]

# ③ お気に入りの切り替え
def toggle_favorite(history_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE history SET favorite = 1 - favorite WHERE id = ?", (history_id,))
    conn.commit()
    conn.close()

# ④ 全履歴削除
def clear_history():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM history")
    conn.commit()
    conn.close()

# ⑤ 最新の履歴を取得
def get_latest_history():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM history ORDER BY search_time DESC LIMIT 1")
    row = cur.fetchone()
    conn.close()
    return row

# ⑥ お気に入りの更新
def update_favorite(history_id, favorite=True):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("UPDATE history SET favorite = ? WHERE id = ?", (int(favorite), history_id))
    conn.commit()
    conn.close()
