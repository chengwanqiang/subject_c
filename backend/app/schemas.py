from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from app.models import TaskStatus


class TaskBase(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str = ""


class TaskCreate(TaskBase):
    status: TaskStatus = TaskStatus.todo


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    position: Optional[int] = Field(default=None, ge=0)


class TaskOut(BaseModel):
    id: int
    title: str
    description: str
    status: TaskStatus
    position: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ReorderPayload(BaseModel):
    # 例如：
    # {
    #   "columns": {
    #     "todo": [1,2],
    #     "doing": [3],
    #     "done": [4,5]
    #   }
    # }
    columns: Dict[TaskStatus, List[int]]
