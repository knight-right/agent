from __future__ import annotations

from app.agents.base import AgentResult, BaseAgent, SharedState


class ReportAgent(BaseAgent):
    name = "report_agent"
    role = "结果汇总与交付输出"
    capabilities = ["总结归档", "交付清单", "管理视图输出", "下一步建议"]

    def act(self, state: SharedState) -> AgentResult:
        qa_report = state.artifacts.get("qa_report", {})
        readiness = "ready" if qa_report.get("score", 0) >= 75 else "needs_improvement"
        artifact = {
            "summary": {
                "goal": state.goal,
                "readiness": readiness,
                "qa_score": qa_report.get("score"),
                "risk_count": len(state.risks),
                "issue_count": len(state.issues),
            },
            "deliverables": list(state.artifacts.keys()),
            "next_actions": [
                "接入真实外部系统API或消息队列",
                "配置企业微信/飞书/邮件告警",
                "为关键动作增加权限与审计校验",
                "增加定时任务和失败重试策略",
            ],
            "decision_log": state.decisions,
            "timeline": state.timeline,
        }
        return AgentResult(
            stage="reporting",
            summary="已生成项目最终交付报告。",
            artifact_key="final_report",
            artifact=artifact,
            metrics={"deliverable_count": len(artifact["deliverables"])},
            decision={"agent": self.name, "decision": f"交付状态：{readiness}"},
        )
