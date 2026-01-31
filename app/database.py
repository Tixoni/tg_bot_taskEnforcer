import sqlite3

DB_NAME = "database.db"

def get_connection():
    return sqlite3.connect(DB_NAME, check_same_thread=False)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            tg_id INTEGER UNIQUE,
            username TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            title TEXT,
            is_completed INTEGER DEFAULT 0
        )
    """)

    conn.commit()
    conn.close()

def add_user(tg_id, username):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR IGNORE INTO users (tg_id, username) VALUES (?, ?)",
        (tg_id, username)
    )
    conn.commit()
    conn.close()

def add_task(user_id, title):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO tasks (user_id, title) VALUES (?, ?)",
        (user_id, title)
    )
    conn.commit()
    conn.close()

def get_user_tasks(user_id):
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, title, is_completed FROM tasks WHERE user_id = ?",
        (user_id,)
    )

    tasks = cursor.fetchall()
    conn.close()
    return [dict(task) for task in tasks]

def toggle_task_status(task_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE tasks SET is_completed = 1 - is_completed WHERE id = ?",
        (task_id,)
    )
    conn.commit()
    conn.close()
