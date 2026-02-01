import os
import psycopg
from psycopg.rows import dict_row

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set")

if "sslmode" not in DATABASE_URL and "railway" in DATABASE_URL.lower():
    DATABASE_URL += "&sslmode=require" if "?" in DATABASE_URL else "?sslmode=require"

def get_connection():
    return psycopg.connect(
        DATABASE_URL,
        row_factory=dict_row,
        connect_timeout=10,
    )

def init_db():
    with get_connection() as conn:
        with conn.cursor() as cur:
            # USERS
            cur.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    tg_id BIGINT UNIQUE NOT NULL,
                    username TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

            # TASKS
            cur.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id SERIAL PRIMARY KEY,
                    user_id BIGINT NOT NULL,
                    title TEXT NOT NULL,
                    is_completed BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (tg_id)
                        ON DELETE CASCADE
                );
            """)

            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_tasks_user_id
                ON tasks(user_id);
            """)

            # HABITS
            # Таблица ПРИВЫЧЕК (HABITS)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS habits (
                    id SERIAL PRIMARY KEY,
                    user_id BIGINT NOT NULL,
                    title TEXT NOT NULL,
                    is_complete_today BOOLEAN DEFAULT FALSE,
                    count_complete INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (tg_id) ON DELETE CASCADE
                );
            """)
            cur.execute("CREATE INDEX IF NOT EXISTS idx_habits_user_id ON habits(user_id);")

# ================= USERS =================

def add_user(tg_id: int, username: str):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO users (tg_id, username)
                VALUES (%s, %s)
                ON CONFLICT (tg_id) DO NOTHING;
            """, (tg_id, username))

# ================= TASKS =================

def add_task(user_id: int, title: str):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO tasks (user_id, title)
                VALUES (%s, %s);
            """, (user_id, title))

def get_user_tasks(user_id: int):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id, title, is_completed
                FROM tasks
                WHERE user_id = %s
                ORDER BY id DESC;
            """, (user_id,))
            return cur.fetchall()

def toggle_task_status(task_id: int):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE tasks
                SET is_completed = NOT is_completed
                WHERE id = %s;
            """, (task_id,))


def delete_completed_tasks():
    """Удаляет все выполненные задачи (вызывается ежедневно в 00:00)."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM tasks WHERE is_completed = TRUE")
            deleted = cur.rowcount
    return deleted

def delete_task(task_id: int):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM tasks WHERE id = %s", (task_id,))

# Редактирование
def update_task_title(task_id: int, new_title: str):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("UPDATE tasks SET title = %s WHERE id = %s", (new_title, task_id))


# ============================ HABITS =================
# Функции для работы с привычками
def add_habit(user_id: int, title: str):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO habits (user_id, title) VALUES (%s, %s)", (user_id, title))

def get_user_habits(user_id: int):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, title, is_complete_today FROM habits WHERE user_id = %s", (user_id,))
            return cur.fetchall()

def toggle_habit_status(habit_id: int):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("UPDATE habits SET is_complete_today = NOT is_complete_today WHERE id = %s", (habit_id,))


def reset_daily_habits():
    """
    Увеличивает count_complete на 1 для всех выполненных сегодня привычек
    и сбрасывает маркер is_complete_today в False для всех привычек.
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            # Сначала увеличиваем счетчик у тех, кто выполнил
            cur.execute("""
                UPDATE habits 
                SET count_complete = count_complete + 1 
                WHERE is_complete_today = TRUE;
            """)
            # Затем сбрасываем статус для всех на следующий день
            cur.execute("UPDATE habits SET is_complete_today = FALSE;")


def delete_habit(habit_id: int):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM habits WHERE id = %s", (habit_id,))


def update_habit_title(habit_id: int, new_title: str):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("UPDATE habits SET title = %s WHERE id = %s", (new_title, habit_id))