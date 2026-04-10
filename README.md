# ai-assistant

独立的 Python Agent 编排层工程，用于为 `personalenglishai` 提供 AI Agent 能力。

当前总体设计见：

- `docs/architecture/ai-assistant-overall-design.md`
- `docs/superpowers/plans/2026-04-10-ai-assistant-bootstrap.md`
- `docs/superpowers/plans/2026-04-10-ai-assistant-phase1-scaffold.md`

## 当前脚手架

当前仓库已经包含最小的 Phase 1 骨架：

- `app/main.py`：FastAPI 应用入口
- `app/api/routes.py`：HTTP 路由
- `app/graphs/agent_graph.py`：LangGraph 占位编排
- `app/tools/registry.py`：工具注册占位
- `app/schemas/agent.py`：请求/响应模型
- `tests/`：最小接口测试

## 本地启动

建议使用项目内虚拟环境：

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m ensurepip --upgrade
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install fastapi httpx langchain-core langgraph pydantic "uvicorn[standard]" pytest
```

运行测试：

```powershell
.\.venv\Scripts\python.exe -m pytest -v
```

启动开发服务：

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

## 环境变量

当前骨架支持以下环境变量：

- `AI_ASSISTANT_BACKEND_BASE_URL`
- `AI_ASSISTANT_BACKEND_TIMEOUT_SECONDS`
- `AI_ASSISTANT_BACKEND_EXPLAIN_PATH`
- `AI_ASSISTANT_REDIS_URL`
- `AI_ASSISTANT_LANGSMITH_ENABLED`
- `AI_ASSISTANT_LANGSMITH_PROJECT`

默认 explain 工具会调用：

- `POST /api/internal/agent-tools/explain`

请求体：

```json
{
  "message": "What is present perfect?"
}
```

响应体：

```json
{
  "reply": "..."
}
```
