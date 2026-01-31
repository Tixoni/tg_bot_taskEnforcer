from fastapi import FastAPI, HTTPException
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

class UserRegistration(BaseModel):
    tg_id: int
    name: str

class TaskCreate(BaseModel):
    user_id: int
    title: str

class TaskResponse(BaseModel):
    id: int
    title: str
    is_completed: int

@app.post("/api/register")
async def register_user(user: UserRegistration):
    try:
        db.add_user(user.tg_id, user.name)
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/tasks/add")
async def add_task(task: TaskCreate):
    db.add_task(task.user_id, task.title)
    return {"status": "ok"}

@app.get("/api/tasks/{user_id}", response_model=List[TaskResponse])
async def get_tasks(user_id: int):
    return db.get_user_tasks(user_id)

@app.post("/api/tasks/toggle/{task_id}")
async def toggle_task(task_id: int):
    db.toggle_task_status(task_id)
    return {"status": "ok"}
