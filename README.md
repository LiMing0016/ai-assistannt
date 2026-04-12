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
- `app/services/assistant_service.py`：统一 assistant 服务
- `app/providers/`：模型 provider 适配层
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

项目支持从仓库根目录的 `.env` 自动读取配置。

推荐做法：

1. 复制 `.env.example` 为 `.env`
2. 在 `.env` 中填入你自己的真实 Kimi key
3. 直接启动服务或在 Jupyter 中调接口

说明：

- `.env.example` 是可提交到仓库的配置模板，只放占位值和注释
- `.env` 是你本地真实配置文件，放真实 key，不提交到 git
- 当前 Phase 1 真正实现并接通的是 `kimi`
- `openai / dashscope` 已在配置层预留，provider 实现后直接接入

当前骨架支持以下环境变量：

- `AI_ASSISTANT_DEFAULT_PROVIDER`
- `AI_ASSISTANT_OPENAI_API_KEY`
- `AI_ASSISTANT_OPENAI_BASE_URL`
- `AI_ASSISTANT_OPENAI_MODEL`
- `AI_ASSISTANT_KIMI_API_KEY`
- `AI_ASSISTANT_KIMI_BASE_URL`
- `AI_ASSISTANT_KIMI_MODEL`
- `AI_ASSISTANT_DASHSCOPE_API_KEY`
- `AI_ASSISTANT_DASHSCOPE_BASE_URL`
- `AI_ASSISTANT_DASHSCOPE_MODEL`
- `AI_ASSISTANT_BACKEND_BASE_URL`
- `AI_ASSISTANT_BACKEND_TIMEOUT_SECONDS`
- `AI_ASSISTANT_BACKEND_EXPLAIN_PATH`
- `AI_ASSISTANT_REDIS_URL`
- `AI_ASSISTANT_LANGSMITH_ENABLED`
- `AI_ASSISTANT_LANGSMITH_PROJECT`

第一版 assistant 默认 provider 为 `kimi`。

`.env.example` 示例：

```dotenv
# 当前默认 provider。Phase 1 先实现 kimi，后续可切到 openai / dashscope
AI_ASSISTANT_DEFAULT_PROVIDER=kimi

# OpenAI 预留配置
AI_ASSISTANT_OPENAI_API_KEY=your-openai-api-key
AI_ASSISTANT_OPENAI_BASE_URL=https://api.openai.com/v1
AI_ASSISTANT_OPENAI_MODEL=gpt-5-mini

# Kimi 配置。真实 key 只写到本地 .env
AI_ASSISTANT_KIMI_API_KEY=your-kimi-key
AI_ASSISTANT_KIMI_BASE_URL=https://api.moonshot.cn/v1
AI_ASSISTANT_KIMI_MODEL=moonshot-v1-8k

# 阿里百炼 / DashScope 预留配置
AI_ASSISTANT_DASHSCOPE_API_KEY=your-dashscope-api-key
AI_ASSISTANT_DASHSCOPE_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
AI_ASSISTANT_DASHSCOPE_MODEL=qwen-plus
```

当前统一聊天入口：

- `POST /assistant/chat`

请求体：

```json
{
  "message": "Explain present perfect simply",
  "conversation_id": "demo-1"
}
```

响应体示例：

```json
{
  "reply": "...",
  "provider": "kimi",
  "model": "moonshot-v1-8k",
  "processor": "assistant",
  "trace_id": "...",
  "tracing": {
    "langsmith_enabled": false,
    "project": null
  },
  "state": {
    "conversation_enabled": true,
    "task_state_enabled": true
  }
}
```

## Jupyter 测试

当 `.env` 已配置好后，直接启动服务：

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

然后在 Jupyter 中请求：

```python
import requests

resp = requests.post(
    "http://127.0.0.1:8000/assistant/chat",
    json={
        "message": "Explain present perfect in Chinese",
        "conversation_id": "demo-1",
    },
    timeout=30,
)

resp.status_code, resp.json()
```

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
