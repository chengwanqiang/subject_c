from __future__ import annotations

import os
import time
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker


def _build_database_url() -> str:
    # 优先使用 DATABASE_URL（便于容器环境统一配置）
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        return database_url

    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "3306")
    name = os.getenv("DB_NAME", "kanban")
    user = os.getenv("DB_USER", "kanban")
    password = os.getenv("DB_PASSWORD", "kanbanpass")
    return f"mysql+pymysql://{user}:{password}@{host}:{port}/{name}?charset=utf8mb4"


DATABASE_URL = _build_database_url()

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=1800,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def wait_for_db(max_wait_seconds: int = 60) -> None:
    """容器启动时 MySQL 可能尚未就绪，这里做简单重试。"""
    deadline = time.time() + max_wait_seconds
    last_err: Exception | None = None
    while time.time() < deadline:
        try:
            with engine.connect() as conn:
                conn.exec_driver_sql("SELECT 1")
            return
        except Exception as e:  # noqa: BLE001 - 启动等待阶段保留原异常信息
            last_err = e
            time.sleep(1)
    raise RuntimeError(f"Database not ready after {max_wait_seconds}s: {last_err}")
