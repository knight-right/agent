from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def now() -> datetime:
    return datetime.utcnow()


class TaskRecord(Base):
    __tablename__ = "tasks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title: Mapped[str] = mapped_column(String(200))
    goal: Mapped[str] = mapped_column(Text)
    context_json: Mapped[str] = mapped_column(Text, default="{}")
    status: Mapped[str] = mapped_column(String(50), default="created")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=now, onupdate=now)

    runs: Mapped[list[WorkflowRun]] = relationship("WorkflowRun", back_populates="task", cascade="all, delete-orphan")
    events: Mapped[list[TaskEvent]] = relationship("TaskEvent", back_populates="task", cascade="all, delete-orphan")


class WorkflowRun(Base):
    __tablename__ = "workflow_runs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    task_id: Mapped[str] = mapped_column(String(36), ForeignKey("tasks.id"), index=True)
    status: Mapped[str] = mapped_column(String(50), default="running")
    final_report_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    task: Mapped[TaskRecord] = relationship("TaskRecord", back_populates="runs")
    events: Mapped[list[TaskEvent]] = relationship("TaskEvent", back_populates="run", cascade="all, delete-orphan")


class TaskEvent(Base):
    __tablename__ = "task_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    task_id: Mapped[str] = mapped_column(String(36), ForeignKey("tasks.id"), index=True)
    run_id: Mapped[str] = mapped_column(String(36), ForeignKey("workflow_runs.id"), index=True)
    agent_name: Mapped[str] = mapped_column(String(100))
    stage: Mapped[str] = mapped_column(String(100))
    content_json: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now)

    task: Mapped[TaskRecord] = relationship("TaskRecord", back_populates="events")
    run: Mapped[WorkflowRun] = relationship("WorkflowRun", back_populates="events")
