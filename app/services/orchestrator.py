from __future__ import annotations

from datetime import datetime
from typing import Iterable

from sqlalchemy.orm import Session

from app.agents.analyst import AnalystAgent
from app.agents.automation import AutomationAgent
from app.agents.base import BaseAgent, SharedState
from app.agents.coordinator import CoordinatorAgent
from app.agents.executor import ExecutorAgent
from app.agents.planner import PlannerAgent
from app.agents.qa import QualityAssuranceAgent
from app.agents.reporter import ReportAgent
from app.models import TaskEvent, TaskRecord, WorkflowRun
from app.utils.json_utils import from_json, to_json


class MultiAgentOrchestrator:
    def __init__(self) -> None:
        self.agents: list[BaseAgent] = [
            PlannerAgent(),
            AnalystAgent(),
            CoordinatorAgent(),
            AutomationAgent(),
            ExecutorAgent(),
            QualityAssuranceAgent(),
            ReportAgent(),
        ]

    def list_agents(self) -> list[dict]:
        return [agent.describe() for agent in self.agents]

    def execute_task(self, db: Session, task: TaskRecord) -> WorkflowRun:
        task.status = "running"
        run = WorkflowRun(task_id=task.id, status="running")
        db.add(run)
        db.flush()

        state = SharedState(goal=task.goal, context=from_json(task.context_json) or {})
        execution_chain = self.agents[:-1]  # report_agent单独放最后，可能在反馈后执行

        for agent in execution_chain:
            result = agent.act(state)
            self._apply_result(db, task, run, state, agent, result)

        qa_score = state.artifacts.get("qa_report", {}).get("score", 0)
        if qa_score < 75:
            # 简单反馈回路：问题清单存在时，重新规划、自动化、执行，再次QA
            feedback_chain: Iterable[BaseAgent] = [PlannerAgent(), AutomationAgent(), ExecutorAgent(), QualityAssuranceAgent()]
            for agent in feedback_chain:
                result = agent.act(state)
                self._apply_result(db, task, run, state, agent, result)

        report_agent = ReportAgent()
        result = report_agent.act(state)
        self._apply_result(db, task, run, state, report_agent, result)

        run.final_report_json = to_json(state.artifacts.get("final_report", {}))
        run.status = "completed"
        run.completed_at = datetime.utcnow()
        task.status = "completed"
        db.commit()
        db.refresh(run)
        return run

    def _apply_result(
        self,
        db: Session,
        task: TaskRecord,
        run: WorkflowRun,
        state: SharedState,
        agent: BaseAgent,
        result,
    ) -> None:
        state.artifacts[result.artifact_key] = result.artifact
        state.issues.extend([item for item in result.new_issues if item not in state.issues])
        state.risks.extend([item for item in result.new_risks if item not in state.risks])
        state.metrics.update(result.metrics)
        if result.decision:
            state.decisions.append(result.decision)
        state.timeline.append(f"{agent.name}: {result.summary}")

        event = TaskEvent(
            task_id=task.id,
            run_id=run.id,
            agent_name=agent.name,
            stage=result.stage,
            content_json=to_json(
                {
                    "summary": result.summary,
                    "artifact_key": result.artifact_key,
                    "artifact": result.artifact,
                    "issues": result.new_issues,
                    "risks": result.new_risks,
                    "metrics": result.metrics,
                    "decision": result.decision,
                }
            ),
        )
        db.add(event)
        task.updated_at = datetime.utcnow()
        db.flush()
