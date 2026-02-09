from __future__ import annotations

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app import crud
from app.db import get_db, wait_for_db
from app.models import Base
from app.schemas import ReorderPayload, TaskCreate, TaskOut, TaskUpdate
from app.db import engine


class UTF8JSONResponse(JSONResponse):
    media_type = "application/json; charset=utf-8"


app = FastAPI(title="Kanban API", version="1.0.0", default_response_class=UTF8JSONResponse)

# docker compose 下我们通过 Nginx 反代 /api，基本不会触发 CORS；
# 但保留宽松配置，方便本地开发时直接访问 8000。
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    wait_for_db(max_wait_seconds=60)
    Base.metadata.create_all(bind=engine)


@app.get("/api/health")
def health() -> dict:
    return {"ok": True}


@app.get("/api/tasks", response_model=list[TaskOut])
def api_list_tasks(db: Session = Depends(get_db)) -> list[TaskOut]:
    return crud.list_tasks(db)


@app.post("/api/tasks", response_model=TaskOut, status_code=201)
def api_create_task(payload: TaskCreate, db: Session = Depends(get_db)) -> TaskOut:
    return crud.create_task(
        db,
        title=payload.title,
        description=payload.description,
        status=payload.status,
    )


@app.patch("/api/tasks/{task_id}", response_model=TaskOut)
def api_update_task(task_id: int, payload: TaskUpdate, db: Session = Depends(get_db)) -> TaskOut:
    task = crud.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return crud.update_task(
        db,
        task=task,
        title=payload.title,
        description=payload.description,
        status=payload.status,
        position=payload.position,
    )


@app.delete("/api/tasks/{task_id}", status_code=204)
def api_delete_task(task_id: int, db: Session = Depends(get_db)) -> None:
    task = crud.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    crud.delete_task(db, task=task)
    return None


@app.post("/api/tasks/reorder", status_code=204)
def api_reorder_tasks(payload: ReorderPayload, db: Session = Depends(get_db)) -> None:
    crud.reorder_tasks(db, payload.columns)
    return None
