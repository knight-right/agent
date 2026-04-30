from __future__ import annotations

from app.agents.base import AgentResult, BaseAgent, SharedState


class AnalystAgent(BaseAgent):
    name = "analyst_agent"
    role = "需求分析与KPI定义"
    capabilities = ["需求梳理", "关键人识别", "约束识别", "成功指标定义"]

    def act(self, state: SharedState) -> AgentResult:
        context = state.context
        stakeholders = context.get("stakeholders") or ["运营负责人", "执行团队", "数据分析角色"]
        kpis = context.get("kpis") or self._default_kpis(state.goal)
        assumptions = context.get("assumptions") or [
            "数据来源可用",
            "执行角色具备基础权限",
            "自动化节点允许定时与事件触发",
        ]
        risks = [
            "输入信息不完整会影响任务拆解质量",
            "跨部门依赖未确认可能导致节点阻塞",
        ]

        artifact = {
            "stakeholders": stakeholders,
            "success_kpis": kpis,
            "assumptions": assumptions,
            "input_contract": {
                "required": ["goal"],
                "optional": ["budget", "deadline", "channels", "team_size", "products", "user_segments"],
            },
            "output_contract": ["计划", "资源分工", "自动化规则", "执行SOP", "QA报告", "最终报告"],
        }
        return AgentResult(
            stage="analysis",
            summary="已提炼关键干系人、假设条件与KPI。",
            artifact_key="analysis",
            artifact=artifact,
            new_risks=risks,
            metrics={"kpi_count": len(kpis), "stakeholder_count": len(stakeholders)},
            decision={"agent": self.name, "decision": "先定义成功指标，再驱动后续Agent输出"},
        )

    @staticmethod
    def _default_kpis(goal: str) -> list[dict]:
        text = goal.lower()
        if any(k in text for k in ["增长", "拉新", "转化", "campaign", "投放"]):
            return [
                {"name": "转化率", "target": ">= 3%"},
                {"name": "获客成本", "target": "持续下降"},
                {"name": "ROI", "target": ">= 1.5"},
            ]
        if any(k in text for k in ["客服", "工单", "服务"]):
            return [
                {"name": "首次响应时长", "target": "< 10分钟"},
                {"name": "一次解决率", "target": ">= 75%"},
                {"name": "满意度", "target": ">= 90%"},
            ]
        return [
            {"name": "按期完成率", "target": ">= 95%"},
            {"name": "自动化覆盖率", "target": ">= 70%"},
            {"name": "异常回滚成功率", "target": ">= 99%"},
        ]
