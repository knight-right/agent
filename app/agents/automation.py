from __future__ import annotations

from app.agents.base import AgentResult, BaseAgent, SharedState


class AutomationAgent(BaseAgent):
    name = "automation_agent"
    role = "自动化流程编排"
    capabilities = ["规则引擎", "触发器设计", "异常处理", "回滚策略"]

    def act(self, state: SharedState) -> AgentResult:
        task_type = state.artifacts.get("plan", {}).get("task_type", "general_ops")
        rules = self._build_rules(task_type, state.context)
        if state.issues:
            rules.append(
                {
                    "name": "qa_issue_handler",
                    "trigger": "qa_report.generated",
                    "condition": "存在未关闭问题",
                    "action": "回流到planner_agent与executor_agent进行修正",
                    "rollback": "保留上一版可执行方案",
                }
            )

        artifact = {
            "engine": "event-driven blackboard",
            "rules": rules,
            "fallback_strategy": [
                "关键节点超时后发送预警",
                "执行失败自动记录失败原因",
                "高风险动作支持人工确认后重试",
            ],
            "audit_fields": ["task_id", "run_id", "agent_name", "stage", "timestamp", "status"],
        }
        return AgentResult(
            stage="automation",
            summary="已生成事件驱动型自动化规则和回滚策略。",
            artifact_key="automation",
            artifact=artifact,
            new_risks=["外部系统事件延迟会影响链路时效"],
            metrics={"rule_count": len(rules), "automation_coverage": "高"},
            decision={"agent": self.name, "decision": "采用事件触发 + 状态审计的自动化编排方式"},
        )

    @staticmethod
    def _build_rules(task_type: str, context: dict) -> list[dict]:
        common = [
            {
                "name": "task_created",
                "trigger": "task.created",
                "condition": "任务状态为created",
                "action": "调用planner_agent和analyst_agent开始准备",
                "rollback": "无",
            },
            {
                "name": "resource_ready",
                "trigger": "analysis.completed",
                "condition": "KPI与约束已生成",
                "action": "调用coordinator_agent分配资源",
                "rollback": "重新进入analysis",
            },
            {
                "name": "execution_ready",
                "trigger": "automation.completed",
                "condition": "规则数量大于0",
                "action": "调用executor_agent输出SOP并准备执行",
                "rollback": "保持上一个稳定版本",
            },
        ]
        if task_type == "campaign_ops":
            common.extend(
                [
                    {
                        "name": "material_review",
                        "trigger": "executor.material_prepared",
                        "condition": "素材齐全",
                        "action": "进入渠道发布",
                        "rollback": "退回素材审核",
                    },
                    {
                        "name": "daily_optimization",
                        "trigger": "cron.daily",
                        "condition": "投放进行中",
                        "action": "根据ROI自动调整预算建议",
                        "rollback": "恢复昨日预算",
                    },
                ]
            )
        elif task_type == "customer_service_ops":
            common.extend(
                [
                    {
                        "name": "ticket_triage",
                        "trigger": "ticket.created",
                        "condition": "工单进入系统",
                        "action": "按优先级和类型自动分流",
                        "rollback": "转入人工客服池",
                    },
                    {
                        "name": "sla_breach_alarm",
                        "trigger": "timer.5min",
                        "condition": "高优工单未响应",
                        "action": "发送升级通知",
                        "rollback": "无",
                    },
                ]
            )
        else:
            common.append(
                {
                    "name": "ops_checkpoint",
                    "trigger": "cron.daily",
                    "condition": "存在进行中的运营任务",
                    "action": "更新看板并记录进度",
                    "rollback": "跳过本轮更新",
                }
            )
        if context.get("compliance"):
            common.append(
                {
                    "name": "compliance_review",
                    "trigger": "before.publish",
                    "condition": f"满足合规要求: {context['compliance']}",
                    "action": "保留审计痕迹并执行发布",
                    "rollback": "拒绝发布并通知负责人",
                }
            )
        return common
