from __future__ import annotations

from app.agents.base import AgentResult, BaseAgent, SharedState


class ExecutorAgent(BaseAgent):
    name = "executor_agent"
    role = "执行落地与SOP生成"
    capabilities = ["执行计划", "操作清单", "渠道动作编排", "异常处置"]

    def act(self, state: SharedState) -> AgentResult:
        task_type = state.artifacts.get("plan", {}).get("task_type", "general_ops")
        sop = self._build_sop(task_type, state.context, bool(state.issues))
        artifact = {
            "sop": sop,
            "runbook": [
                "准备输入数据",
                "执行自动化触发",
                "人工确认关键节点",
                "监控异常与回滚",
                "沉淀结果与经验",
            ],
            "handoff_checklist": [
                "确认输入完整",
                "确认负责人在线",
                "确认异常通知配置生效",
                "确认日志写入成功",
            ],
        }
        return AgentResult(
            stage="execution",
            summary="已输出可执行SOP与交接检查清单。",
            artifact_key="execution_playbook",
            artifact=artifact,
            new_issues=["建议补充真实外部系统API接入"],
            metrics={"sop_steps": len(sop)},
            decision={"agent": self.name, "decision": "使用标准SOP保证可复制执行"},
        )

    @staticmethod
    def _build_sop(task_type: str, context: dict, has_feedback: bool) -> list[dict]:
        if task_type == "campaign_ops":
            steps = [
                {"step": 1, "action": "导入用户分群与渠道预算", "owner": "运营执行专员"},
                {"step": 2, "action": "检查素材状态并发起审批", "owner": "内容/设计"},
                {"step": 3, "action": "触发渠道投放自动化规则", "owner": "自动化工程师"},
                {"step": 4, "action": "每日跟踪ROI/CVR并输出调整建议", "owner": "数据分析角色"},
                {"step": 5, "action": "复盘转化结果并沉淀策略模板", "owner": "项目经理"},
            ]
        elif task_type == "customer_service_ops":
            steps = [
                {"step": 1, "action": "接收工单并自动打标签", "owner": "客服系统"},
                {"step": 2, "action": "按优先级与技能组分配工单", "owner": "自动化工程师"},
                {"step": 3, "action": "异常或VIP工单转人工处理", "owner": "客服主管"},
                {"step": 4, "action": "定时检查SLA并预警", "owner": "项目协调员"},
                {"step": 5, "action": "汇总满意度和关闭率报告", "owner": "数据分析角色"},
            ]
        else:
            steps = [
                {"step": 1, "action": "接收运营目标与上下文", "owner": "业务分析师"},
                {"step": 2, "action": "按计划生成执行动作清单", "owner": "运营执行专员"},
                {"step": 3, "action": "触发自动化编排并跟踪状态", "owner": "自动化工程师"},
                {"step": 4, "action": "记录异常并通知负责人", "owner": "项目协调员"},
                {"step": 5, "action": "输出日报与阶段复盘", "owner": "项目经理"},
            ]
        if has_feedback:
            steps.append({"step": len(steps) + 1, "action": "根据QA反馈补充缺失项并重新执行校验", "owner": "运营执行专员"})
        if context.get("channels"):
            steps.append({"step": len(steps) + 1, "action": f"同步渠道列表：{context['channels']}", "owner": "运营执行专员"})
        return steps
