from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class TaskCreate(BaseModel):
    title: str = Field(..., description="任务标题")
    goal: str = Field(..., description="任务目标")
    context: dict[str, Any] = Field(default_factory=dict, description="上下文信息")
    auto_run: bool = Field(default=True, description="是否创建后自动执行")


class TaskResponse(BaseModel):
    id: str
    title: str
    goal: str
    context: dict[str, Any]
    status: str
    created_at: datetime
    updated_at: datetime


class AgentDescriptor(BaseModel):
    name: str
    role: str
    capabilities: list[str]


class EventResponse(BaseModel):
    id: int
    task_id: str
    run_id: str
    agent_name: str
    stage: str
    content: dict[str, Any]
    created_at: datetime


class RunResponse(BaseModel):
    id: str
    task_id: str
    status: str
    final_report: dict[str, Any] | None
    created_at: datetime
    completed_at: datetime | None


class TaskDetailResponse(BaseModel):
    task: TaskResponse
    latest_run: RunResponse | None
    events: list[EventResponse]


class SharedStateResponse(BaseModel):
    goal: str
    context: dict[str, Any]
    artifacts: dict[str, Any]
    issues: list[str]
    risks: list[str]
    metrics: dict[str, Any]
    decisions: list[dict[str, Any]]
    timeline: list[str]
