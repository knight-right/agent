from __future__ import annotations

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import Base, engine, get_db
from app.models import TaskEvent, TaskRecord, WorkflowRun
from app.schemas import (
    AgentDescriptor,
    EventResponse,
    RunResponse,
    TaskCreate,
    TaskDetailResponse,
    TaskResponse,
)
from app.services.orchestrator import MultiAgentOrchestrator
from app.utils.json_utils import from_json, to_json

app = FastAPI(
    title="Multi-Agent 协同运营自动化系统",
    version="1.0.0",
    description="一个基于共享黑板和工作流编排的多Agent协同运营自动化后端示例。",
)

Base.metadata.create_all(bind=engine)
orchestrator = MultiAgentOrchestrator()


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "multi-agent-ops-system"}


@app.get("/api/agents", response_model=list[AgentDescriptor])
def list_agents() -> list[dict]:
    return orchestrator.list_agents()


@app.post("/api/tasks", response_model=TaskDetailResponse)
def create_task(payload: TaskCreate, db: Session = Depends(get_db)) -> TaskDetailResponse:
    task = TaskRecord(
        title=payload.title,
        goal=payload.goal,
        context_json=to_json(payload.context),
        status="created",
    )
    db.add(task)
    db.commit()
    db.refresh(task)

    latest_run = None
    if payload.auto_run:
        latest_run = orchestrator.execute_task(db, task)

    return build_task_detail(db, task.id)


@app.post("/api/tasks/{task_id}/execute", response_model=RunResponse)
def execute_task(task_id: str, db: Session = Depends(get_db)) -> RunResponse:
    task = db.get(TaskRecord, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    run = orchestrator.execute_task(db, task)
    return RunResponse(
        id=run.id,
        task_id=run.task_id,
        status=run.status,
        final_report=from_json(run.final_report_json),
        created_at=run.created_at,
        completed_at=run.completed_at,
    )


@app.get("/api/tasks", response_model=list[TaskResponse])
def list_tasks(db: Session = Depends(get_db)) -> list[TaskResponse]:
    tasks = db.scalars(select(TaskRecord).order_by(TaskRecord.created_at.desc())).all()
    return [
        TaskResponse(
            id=task.id,
            title=task.title,
            goal=task.goal,
            context=from_json(task.context_json),
            status=task.status,
            created_at=task.created_at,
            updated_at=task.updated_at,
        )
        for task in tasks
    ]


@app.get("/api/tasks/{task_id}", response_model=TaskDetailResponse)
def get_task(task_id: str, db: Session = Depends(get_db)) -> TaskDetailResponse:
    return build_task_detail(db, task_id)


@app.get("/api/tasks/{task_id}/events", response_model=list[EventResponse])
def list_events(task_id: str, db: Session = Depends(get_db)) -> list[EventResponse]:
    task = db.get(TaskRecord, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    events = db.scalars(
        select(TaskEvent).where(TaskEvent.task_id == task_id).order_by(TaskEvent.created_at.asc(), TaskEvent.id.asc())
    ).all()
    return [
        EventResponse(
            id=event.id,
            task_id=event.task_id,
            run_id=event.run_id,
            agent_name=event.agent_name,
            stage=event.stage,
            content=from_json(event.content_json),
            created_at=event.created_at,
        )
        for event in events
    ]


@app.get("/api/runs", response_model=list[RunResponse])
def list_runs(db: Session = Depends(get_db)) -> list[RunResponse]:
    runs = db.scalars(select(WorkflowRun).order_by(WorkflowRun.created_at.desc())).all()
    return [
        RunResponse(
            id=run.id,
            task_id=run.task_id,
            status=run.status,
            final_report=from_json(run.final_report_json),
            created_at=run.created_at,
            completed_at=run.completed_at,
        )
        for run in runs
    ]


def build_task_detail(db: Session, task_id: str) -> TaskDetailResponse:
    task = db.get(TaskRecord, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    latest_run = db.scalars(
        select(WorkflowRun).where(WorkflowRun.task_id == task_id).order_by(WorkflowRun.created_at.desc())
    ).first()
    events = db.scalars(
        select(TaskEvent).where(TaskEvent.task_id == task_id).order_by(TaskEvent.created_at.asc(), TaskEvent.id.asc())
    ).all()

    task_resp = TaskResponse(
        id=task.id,
        title=task.title,
        goal=task.goal,
        context=from_json(task.context_json),
        status=task.status,
        created_at=task.created_at,
        updated_at=task.updated_at,
    )
    run_resp = None
    if latest_run:
        run_resp = RunResponse(
            id=latest_run.id,
            task_id=latest_run.task_id,
            status=latest_run.status,
            final_report=from_json(latest_run.final_report_json),
            created_at=latest_run.created_at,
            completed_at=latest_run.completed_at,
        )
    event_resp = [
        EventResponse(
            id=event.id,
            task_id=event.task_id,
            run_id=event.run_id,
            agent_name=event.agent_name,
            stage=event.stage,
            content=from_json(event.content_json),
            created_at=event.created_at,
        )
        for event in events
    ]
    return TaskDetailResponse(task=task_resp, latest_run=run_resp, events=event_resp)
