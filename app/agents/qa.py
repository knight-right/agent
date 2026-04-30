from __future__ import annotations

from app.agents.base import AgentResult, BaseAgent, SharedState


class QualityAssuranceAgent(BaseAgent):
    name = "qa_agent"
    role = "质量校验与风险审查"
    capabilities = ["完整性检查", "一致性校验", "风险识别", "修复建议"]

    def act(self, state: SharedState) -> AgentResult:
        required = ["plan", "analysis", "resource_plan", "automation", "execution_playbook"]
        missing = [key for key in required if key not in state.artifacts]
        issues = list(missing)

        if "analysis" in state.artifacts and not state.artifacts["analysis"].get("success_kpis"):
            issues.append("analysis.success_kpis 缺失")
        if "automation" in state.artifacts and not state.artifacts["automation"].get("rules"):
            issues.append("automation.rules 为空")
        if "execution_playbook" in state.artifacts and not state.artifacts["execution_playbook"].get("sop"):
            issues.append("execution_playbook.sop 为空")

        score = max(0, 100 - len(issues) * 18 - len(state.risks) * 3)
        artifact = {
            "score": score,
            "missing_items": missing,
            "issues": issues,
            "review_points": [
                "每个阶段都有明确负责人",
                "自动化规则存在回滚策略",
                "SOP可以被执行团队复用",
                "关键指标可被跟踪",
            ],
            "recommendations": self._recommendations(issues),
        }
        return AgentResult(
            stage="qa",
            summary="已完成质量扫描并生成问题与建议。",
            artifact_key="qa_report",
            artifact=artifact,
            new_issues=issues,
            new_risks=["若未接入真实消息/任务系统，生产可用性仍需验证"],
            metrics={"qa_score": score},
            decision={"agent": self.name, "decision": f"当前方案质量分 {score}"},
        )

    @staticmethod
    def _recommendations(issues: list[str]) -> list[str]:
        if not issues:
            return ["可以进入试运行阶段", "建议补充灰度发布与真实监控告警"]
        return [f"修复问题：{item}" for item in issues]
