# Multi-Agent 协同运营自动化系统

这是一个可直接运行的 **多 Agent 协同运营自动化后端项目**，采用：

- **FastAPI**：提供 REST API
- **SQLAlchemy + SQLite**：任务、运行记录、事件日志持久化
- **共享黑板（Shared Blackboard）**：Agent 间共享状态
- **工作流编排器（Orchestrator）**：按阶段调度 Agent，支持简单反馈回路

## 功能特性

- 多 Agent 协同：规划、分析、协调、自动化、执行、质检、汇总
- 创建任务后自动执行
- 自动记录每个 Agent 的产物与事件日志
- 支持查看任务详情、执行记录、Agent 列表
- 支持 QA 低分时自动触发修订回路

## 项目结构

```bash
multi_agent_ops_system/
├── app/
│   ├── agents/
│   │   ├── analyst.py
│   │   ├── automation.py
│   │   ├── base.py
│   │   ├── coordinator.py
│   │   ├── executor.py
│   │   ├── planner.py
│   │   ├── qa.py
│   │   └── reporter.py
│   ├── services/
│   │   └── orchestrator.py
│   ├── utils/
│   │   └── json_utils.py
│   ├── database.py
│   ├── main.py
│   ├── models.py
│   └── schemas.py
├── tests/
├── README.md
└── requirements.txt
```

## 安装运行

### 1）创建虚拟环境

```bash
python -m venv .venv
```

### 2）激活环境

Windows:

```bash
.venv\Scripts\activate
```

macOS / Linux:

```bash
source .venv/bin/activate
```

### 3）安装依赖

```bash
pip install -r requirements.txt
```

### 4）启动服务

```bash
uvicorn app.main:app --reload
```

启动后访问：

- Swagger 文档：`http://127.0.0.1:8000/docs`
- 健康检查：`http://127.0.0.1:8000/health`

## API 示例

### 查看 Agent 列表

```bash
curl http://127.0.0.1:8000/api/agents
```

### 创建并自动执行任务

```bash
curl -X POST http://127.0.0.1:8000/api/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "title": "618营销协同自动化",
    "goal": "为618大促设计一个多agent协同运营自动化流程",
    "context": {
      "budget": "100000",
      "deadline": "2026-06-01",
      "channels": ["公众号", "短信", "小红书", "私域社群"],
      "team_size": 5,
      "stakeholders": ["市场负责人", "运营经理", "数据分析师"],
      "kpis": [
        {"name": "ROI", "target": ">= 2.0"},
        {"name": "转化率", "target": ">= 4%"}
      ],
      "compliance": "广告法审查"
    },
    "auto_run": true
  }'
```

### 查询任务详情

```bash
curl http://127.0.0.1:8000/api/tasks/{task_id}
```

### 查询任务事件

```bash
curl http://127.0.0.1:8000/api/tasks/{task_id}/events
```

## 协作流程

默认执行顺序：

1. `planner_agent`：拆解任务、规划阶段
2. `analyst_agent`：分析需求、提炼 KPI
3. `coordinator_agent`：协调资源、制定交接 SLA
4. `automation_agent`：生成自动化规则
5. `executor_agent`：生成执行 SOP
6. `qa_agent`：校验质量与风险
7. `report_agent`：汇总报告

若 `qa_score < 75`，会自动触发：

- `planner_agent`
- `automation_agent`
- `executor_agent`
- `qa_agent`

再进入一次修订回路，最后生成汇总报告。

## 你可以继续扩展的方向

- 接入真实大模型（OpenAI / Azure OpenAI / 本地模型）
- 接入 Redis / RabbitMQ / Kafka 实现异步任务编排
- 接入企业微信、飞书、钉钉、邮件告警
- 接入 Airflow / Celery 做定时调度
- 增加 RBAC 权限控制、审计日志、灰度发布
- 增加前端管理台（Vue / React）
