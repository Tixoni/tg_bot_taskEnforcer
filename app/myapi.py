from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import app.database as db

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# [cite_start]Модели данных [cite: 36]
class UserRegistration(BaseModel): # Вернули модель
    tg_id: int
    name: str

class TaskCreate(BaseModel):
    user_id: int
    title: str

class TaskResponse(BaseModel):
    id: int
    title: str
    is_completed: int

# Эндпоинт регистрации (Вернули его!)
@app.post("/api/register")
async def register_user(user_data: UserRegistration):
    db.add_user(user_data.tg_id, user_data.name)
    return {"status": "success", "message": f"User {user_data.name} saved"}

# Эндпоинты задач
@app.post("/api/tasks/add")
async def api_add_task(task: TaskCreate):
    db.add_task(task.user_id, task.title) # Теперь AttributeError не будет
    return {"status": "success", "message": "Task added"}

@app.get("/api/tasks/{user_id}", response_model=List[TaskResponse])
async def api_get_tasks(user_id: int):
    tasks = db.get_user_tasks(user_id)
    return tasks

@app.post("/api/tasks/toggle/{task_id}")
async def api_toggle_task(task_id: int):
    db.toggle_task_status(task_id)
    return {"status": "success"}