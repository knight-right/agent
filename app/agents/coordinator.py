from __future__ import annotations

from app.agents.base import AgentResult, BaseAgent, SharedState


class CoordinatorAgent(BaseAgent):
    name = "coordinator_agent"
    role = "资源协调与责任分配"
    capabilities = ["角色分工", "排期", "依赖管理", "资源冲突识别"]

    def act(self, state: SharedState) -> AgentResult:
        analysis = state.artifacts.get("analysis", {})
        plan = state.artifacts.get("plan", {})
        stakeholders = analysis.get("stakeholders", ["运营负责人", "数据分析角色", "执行团队"])
        phases = plan.get("phases", [])

        assignments = []
        owners = {
            "analyst_agent": "业务分析师",
            "coordinator_agent": "项目协调员",
            "automation_agent": "自动化工程师",
            "executor_agent": "运营执行专员",
            "qa_agent": "质量负责人",
            "report_agent": "项目经理",
            "planner_agent": "架构规划师",
        }
        for i, phase in enumerate(phases, start=1):
            assignments.append(
                {
                    "phase": phase["name"],
                    "owner": owners.get(phase["owner"], phase["owner"]),
                    "sla": f"T+{i} 天",
                    "handoff": phase["depends_on"],
                }
            )

        artifact = {
            "stakeholders": stakeholders,
            "assignments": assignments,
            "communication_mechanism": [
                "每个阶段完成后写入共享黑板",
                "高风险问题升级给协调员",
                "QA未通过时自动触发修订回路",
            ],
            "resource_warnings": self._detect_warnings(state.context),
        }
        return AgentResult(
            stage="coordination",
            summary="已完成资源分工、SLA和交接机制设计。",
            artifact_key="resource_plan",
            artifact=artifact,
            new_issues=artifact["resource_warnings"],
            metrics={"assignment_count": len(assignments)},
            decision={"agent": self.name, "decision": "采用共享黑板 + 阶段交接的协同模式"},
        )

    @staticmethod
    def _detect_warnings(context: dict) -> list[str]:
        warnings = []
        team_size = context.get("team_size")
        if isinstance(team_size, int) and team_size < 3:
            warnings.append("团队规模小于3，建议提高自动化覆盖率以降低人力压力")
        if not context.get("deadline"):
            warnings.append("未指定deadline，默认按标准节奏执行")
        return warnings
