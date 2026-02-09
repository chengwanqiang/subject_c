from __future__ import annotations

from typing import Dict, List, Optional

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Task, TaskStatus


def list_tasks(db: Session) -> List[Task]:
    stmt = select(Task).order_by(Task.status.asc(), Task.position.asc(), Task.id.asc())
    return list(db.scalars(stmt).all())


def get_task(db: Session, task_id: int) -> Optional[Task]:
    return db.get(Task, task_id)


def create_task(db: Session, *, title: str, description: str, status: TaskStatus) -> Task:
    max_pos = db.scalar(select(func.max(Task.position)).where(Task.status == status))
    next_pos = int(max_pos or -1) + 1
    task = Task(title=title, description=description, status=status, position=next_pos)
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def update_task(
    db: Session,
    *,
    task: Task,
    title: Optional[str] = None,
    description: Optional[str] = None,
    status: Optional[TaskStatus] = None,
    position: Optional[int] = None,
) -> Task:
    if title is not None:
        task.title = title
    if description is not None:
        task.description = description
    if status is not None:
        task.status = status
    if position is not None:
        task.position = position
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def delete_task(db: Session, *, task: Task) -> None:
    db.delete(task)
    db.commit()


def reorder_tasks(db: Session, columns: Dict[TaskStatus, List[int]]) -> None:
    """
    根据前端拖拽后的列顺序，批量更新 status + position。
    期望 columns 覆盖所有任务 id（也允许缺省：缺省任务保持不变）。
    """
    # 拉取现有任务，避免无效 id
    all_ids: List[int] = []
    for ids in columns.values():
        all_ids.extend(ids)
    if not all_ids:
        return

    existing = list(db.scalars(select(Task).where(Task.id.in_(all_ids))).all())
    existing_map = {t.id: t for t in existing}

    for status, ids in columns.items():
        for pos, task_id in enumerate(ids):
            task = existing_map.get(task_id)
            if not task:
                continue
            task.status = status
            task.position = pos
            db.add(task)

    db.commit()
