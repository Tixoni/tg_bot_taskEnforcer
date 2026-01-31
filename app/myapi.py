from pathlib import Path
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List
import app.database as db

app = FastAPI()

# Папка web — рядом с app (родитель app = корень проекта)
WEB_DIR = Path(__file__).resolve().parent.parent / "web"

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ================= MODELS =================

class UserRegistration(BaseModel):
    tg_id: int
    name: str


class TaskCreate(BaseModel):
    user_id: int
    title: str


class TaskResponse(BaseModel):
    id: int
    title: str
    is_completed: bool


class HabitCreate(BaseModel):
    user_id: int
    title: str


class HabitResponse(BaseModel):
    id: int
    title: str
    is_completed_today: bool


# ================= USERS =================

@app.post("/api/register")
async def register_user(user: UserRegistration):
    try:
        db.add_user(user.tg_id, user.name)
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ================= TASKS =================

@app.post("/api/tasks/add")
async def api_add_task(task: TaskCreate):
    db.add_task(task.user_id, task.title)
    return {"status": "ok"}


@app.get("/api/tasks/{user_id}", response_model=List[TaskResponse])
async def api_get_tasks(user_id: int):
    return db.get_user_tasks(user_id)


@app.post("/api/tasks/toggle/{task_id}")
async def api_toggle_task(task_id: int):
    db.toggle_task_status(task_id)
    return {"status": "ok"}


# ================= HABITS =================

@app.post("/api/habits/add")
async def api_add_habit(habit: HabitCreate):
    db.add_habit(habit.user_id, habit.title)
    return {"status": "ok"}


@app.get("/api/habits/{user_id}", response_model=List[HabitResponse])
async def api_get_habits(user_id: int):
    rows = db.get_user_habits(user_id)
    # Всегда возвращаем bool (БД/драйвер может вернуть None для is_completed_today)
    return [
        {"id": r["id"], "title": r["title"], "is_completed_today": bool(r.get("is_completed_today"))}
        for r in rows
    ]


@app.post("/api/habits/toggle/{habit_id}")
async def api_toggle_habit(habit_id: int):
    db.toggle_habit_today(habit_id)
    return {"status": "ok"}


# Проверка работы сервера (для Railway/мониторинга)
@app.get("/health")
async def health():
    return {"status": "ok"}


# Webhook для Telegram (используется при WEBHOOK_BASE_URL) — один инстанс, без Conflict
@app.post("/webhook")
async def telegram_webhook(request: Request):
    bot = getattr(request.app.state, "bot", None)
    dp = getattr(request.app.state, "dp", None)
    if not bot or not dp:
        raise HTTPException(500, "Bot not configured for webhook")
    from aiogram.types import Update
    try:
        body = await request.json()
        update = Update.model_validate(body, context={"bot": bot})
        await dp.feed_update(bot, update)
    except Exception as e:
        raise HTTPException(400, detail=str(e))
    return {"ok": True}


# Раздача веб-приложения с того же хоста (убирает "failed to fetch")
# Подключать после всех /api маршрутов, чтобы они имели приоритет
if WEB_DIR.exists():
    app.mount("/", StaticFiles(directory=str(WEB_DIR), html=True), name="web")
