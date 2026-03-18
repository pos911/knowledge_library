import sqlite3
import datetime
import os
from config import DB_PATH

# DB_PATH가 상대 경로인 경우, 이 파일(database.py) 위치 기준으로 절대경로로 변환
# GitHub Actions runner에서 실행 디렉토리가 달라져도 항상 repo 루트에 DB가 생성되도록 보장
_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if not os.path.isabs(DB_PATH):
    DB_PATH = os.path.join(_BASE_DIR, DB_PATH)


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            link TEXT UNIQUE NOT NULL,
            published_date TEXT NOT NULL,
            content TEXT,
            summary TEXT,
            status TEXT DEFAULT 'pending'
        )
    ''')
    conn.commit()
    conn.close()


def is_post_exists(link):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM posts WHERE link = ?", (link,))
    exists = cursor.fetchone() is not None
    conn.close()
    return exists


def insert_post(title, link, published_date, content):
    if is_post_exists(link):
        return False

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO posts (title, link, published_date, content, status) VALUES (?, ?, ?, ?, 'pending')",
        (title, link, published_date, content)
    )
    conn.commit()
    conn.close()
    return True


def get_pending_posts():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM posts WHERE status = 'pending'")
    posts = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return posts


def update_post_summary(post_id, summary):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE posts SET summary = ?, status = 'summarized' WHERE id = ?",
        (summary, post_id)
    )
    conn.commit()
    conn.close()


def get_summarized_posts():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM posts WHERE status = 'summarized'")
    posts = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return posts


def mark_post_sent(post_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE posts SET status = 'sent' WHERE id = ?", (post_id,))
    conn.commit()
    conn.close()
