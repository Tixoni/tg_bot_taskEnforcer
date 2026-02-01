from pathlib import Path
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List
import app.database as db

app = FastAPI()
WEB_DIR = Path(__file__).resolve().parent.parent / "web"

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

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




@app.post("/api/register")
async def register_user(user: UserRegistration):
    try:
        db.add_user(user.tg_id, user.name)
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/tasks/add")
async def api_add_task(task: TaskCreate):
    try:
        db.add_task(task.user_id, task.title)
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/tasks/{user_id}", response_model=List[TaskResponse])
async def api_get_tasks(user_id: int):
    try:
        return db.get_user_tasks(user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/tasks/toggle/{task_id}")
async def api_toggle_task(task_id: int):
    try:
        db.toggle_task_status(task_id)
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    return {"status": "ok"}


class HabitCreate(BaseModel):
    user_id: int
    title: str

@app.post("/api/habits/add")
async def api_add_habit(habit: HabitCreate):
    db.add_habit(habit.user_id, habit.title)
    return {"status": "ok"}

@app.get("/api/habits/{user_id}")
async def api_get_habits(user_id: int):
    return db.get_user_habits(user_id)

@app.post("/api/habits/toggle/{habit_id}")
async def api_toggle_habit(habit_id: int):
    db.toggle_habit_status(habit_id)
    return {"status": "ok"}



# Эндпоинты удаления
@app.delete("/api/tasks/{task_id}")
async def api_delete_task(task_id: int):
    db.delete_task(task_id)
    return {"status": "ok"}

@app.delete("/api/habits/{habit_id}")
async def api_delete_habit(habit_id: int):
    db.delete_habit(habit_id)
    return {"status": "ok"}

# Эндпоинты редактирования
class UpdateItem(BaseModel):
    title: str

@app.post("/api/tasks/update/{task_id}")
async def api_update_task(task_id: int, data: UpdateItem):
    db.update_task_title(task_id, data.title)
    return {"status": "ok"}

@app.post("/api/habits/update/{habit_id}")
async def api_update_habit(habit_id: int, data: UpdateItem):
    db.update_habit_title(habit_id, data.title)
    return {"status": "ok"}

if WEB_DIR.exists():
    app.mount("/", StaticFiles(directory=str(WEB_DIR), html=True), name="web")