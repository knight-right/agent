from __future__ import annotations

from app.agents.base import AgentResult, BaseAgent, SharedState


class PlannerAgent(BaseAgent):
    name = "planner_agent"
    role = "任务拆解与流程规划"
    capabilities = ["目标解析", "阶段拆解", "里程碑制定", "依赖关系识别"]

    def act(self, state: SharedState) -> AgentResult:
        task_type = self._infer_task_type(state.goal, state.context)
        constraints = self._extract_constraints(state.context)
        phases = self._build_phases(task_type)
        if state.issues:
            phases.append(
                {
                    "name": "优化修正",
                    "owner": "planner_agent",
                    "deliverable": "根据QA问题清单补充遗漏项",
                    "depends_on": ["质量校验"],
                }
            )

        artifact = {
            "task_type": task_type,
            "objective": state.goal,
            "constraints": constraints,
            "phases": phases,
            "milestones": [
                "完成需求分析",
                "形成自动化流程",
                "产出执行SOP",
                "通过质量校验",
                "输出交付报告",
            ],
        }
        return AgentResult(
            stage="planning",
            summary="已完成任务拆解和阶段规划。",
            artifact_key="plan",
            artifact=artifact,
            new_risks=["目标范围变更可能导致流程重排"],
            metrics={"planned_phases": len(phases)},
            decision={"agent": self.name, "decision": f"采用 {task_type} 场景模板进行协同编排"},
        )

    @staticmethod
    def _infer_task_type(goal: str, context: dict) -> str:
        text = f"{goal} {context}".lower()
        if any(k in text for k in ["营销", "campaign", "投放", "拉新", "增长"]):
            return "campaign_ops"
        if any(k in text for k in ["客服", "工单", "售后", "service"]):
            return "customer_service_ops"
        if any(k in text for k in ["电商", "订单", "商品", "库存", "ecommerce"]):
            return "ecommerce_ops"
        if any(k in text for k in ["内容", "新媒体", "文章", "短视频", "公众号"]):
            return "content_ops"
        return "general_ops"

    @staticmethod
    def _extract_constraints(context: dict) -> list[str]:
        candidates = []
        for key in ["budget", "deadline", "team_size", "channels", "region", "compliance"]:
            if key in context:
                candidates.append(f"{key}: {context[key]}")
        if not candidates:
            candidates.append("默认采用通用运营约束：低耦合、可追踪、可回滚")
        return candidates

    @staticmethod
    def _build_phases(task_type: str) -> list[dict]:
        common = [
            {"name": "需求分析", "owner": "analyst_agent", "deliverable": "输入输出边界与KPI定义", "depends_on": []},
            {"name": "资源协调", "owner": "coordinator_agent", "deliverable": "角色分工与排期", "depends_on": ["需求分析"]},
            {"name": "自动化编排", "owner": "automation_agent", "deliverable": "触发器/条件/动作链路", "depends_on": ["资源协调"]},
            {"name": "执行落地", "owner": "executor_agent", "deliverable": "标准作业流程SOP", "depends_on": ["自动化编排"]},
            {"name": "质量校验", "owner": "qa_agent", "deliverable": "风险与缺口清单", "depends_on": ["执行落地"]},
            {"name": "结果汇总", "owner": "report_agent", "deliverable": "最终交付报告", "depends_on": ["质量校验"]},
        ]
        if task_type == "campaign_ops":
            common.insert(3, {"name": "渠道策略", "owner": "executor_agent", "deliverable": "渠道投放节奏与素材需求", "depends_on": ["资源协调"]})
        if task_type == "customer_service_ops":
            common.insert(3, {"name": "服务分流", "owner": "automation_agent", "deliverable": "工单分级与SLA规则", "depends_on": ["资源协调"]})
        return common
