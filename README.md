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
- 当前已支持 `kimi / openai / dashscope`
- 当前已支持“请求级 provider/model 覆盖”
- 会话级模型持久化将在后续接到 conversation state

当前骨架支持以下环境变量：

- `AI_ASSISTANT_DEFAULT_PROVIDER`
- `AI_ASSISTANT_OPENAI_API_KEY`
- `AI_ASSISTANT_OPENAI_BASE_URL`
- `AI_ASSISTANT_OPENAI_MODEL`
- `AI_ASSISTANT_OPENAI_TIMEOUT_SECONDS`
- `AI_ASSISTANT_KIMI_API_KEY`
- `AI_ASSISTANT_KIMI_BASE_URL`
- `AI_ASSISTANT_KIMI_MODEL`
- `AI_ASSISTANT_KIMI_TIMEOUT_SECONDS`
- `AI_ASSISTANT_DASHSCOPE_API_KEY`
- `AI_ASSISTANT_DASHSCOPE_BASE_URL`
- `AI_ASSISTANT_DASHSCOPE_MODEL`
- `AI_ASSISTANT_DASHSCOPE_TIMEOUT_SECONDS`
- `AI_ASSISTANT_BACKEND_BASE_URL`
- `AI_ASSISTANT_BACKEND_TIMEOUT_SECONDS`
- `AI_ASSISTANT_BACKEND_EXPLAIN_PATH`
- `AI_ASSISTANT_BACKEND_TRANSLATE_PATH`
- `AI_ASSISTANT_BACKEND_MODE`
- `AI_ASSISTANT_REDIS_URL`
- `AI_ASSISTANT_LANGSMITH_ENABLED`
- `AI_ASSISTANT_LANGSMITH_PROJECT`
- `AI_ASSISTANT_PROMPT_BASE_DIR`

当前 assistant 默认 provider 仍为 `kimi`，但可以切到 `openai / dashscope`。

`.env.example` 示例：

```dotenv
# 当前默认 provider。Phase 1 先实现 kimi，后续可切到 openai / dashscope
AI_ASSISTANT_DEFAULT_PROVIDER=kimi

# OpenAI 配置
AI_ASSISTANT_OPENAI_API_KEY=your-openai-api-key
AI_ASSISTANT_OPENAI_BASE_URL=https://api.openai.com/v1
AI_ASSISTANT_OPENAI_MODEL=gpt-5-mini
AI_ASSISTANT_OPENAI_TIMEOUT_SECONDS=30

# Kimi 配置。真实 key 只写到本地 .env
AI_ASSISTANT_KIMI_API_KEY=your-kimi-key
AI_ASSISTANT_KIMI_BASE_URL=https://api.moonshot.cn/v1
AI_ASSISTANT_KIMI_MODEL=moonshot-v1-8k
AI_ASSISTANT_KIMI_TIMEOUT_SECONDS=30

# 阿里百炼 / DashScope 配置
AI_ASSISTANT_DASHSCOPE_API_KEY=your-dashscope-api-key
AI_ASSISTANT_DASHSCOPE_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
AI_ASSISTANT_DASHSCOPE_MODEL=qwen-plus
AI_ASSISTANT_DASHSCOPE_TIMEOUT_SECONDS=30

# Java 后端配置
AI_ASSISTANT_BACKEND_MODE=live
AI_ASSISTANT_BACKEND_BASE_URL=http://127.0.0.1:8080
AI_ASSISTANT_BACKEND_TIMEOUT_SECONDS=5
AI_ASSISTANT_BACKEND_EXPLAIN_PATH=/api/internal/agent-tools/explain
AI_ASSISTANT_BACKEND_TRANSLATE_PATH=/api/internal/agent-tools/translate

# Prompt 目录。把 agent 行为模板和反馈模板从 Python 代码中拆出来管理
AI_ASSISTANT_PROMPT_BASE_DIR=prompts
```

## Prompt 资产

当前 translation agent 的 prompt 资产已独立到仓库 `prompts/` 目录：

- `prompts/translation/system.md`
- `prompts/translation/diagnosis.md`
- `prompts/translation/feedback/*.md`

代码侧分工：

- `app/agents/english/translation_agent.py`
  - 负责编排翻译、诊断和画像更新
- `app/prompting/loader.py`
  - 负责从磁盘读取模板
- `app/prompting/renderer.py`
  - 负责变量注入和渲染

这样后续扩展不同学段、不同 agent、不同 prompt 版本时，不需要继续把大段策略文本硬编码进 Python 文件。

后端模式说明：

- `AI_ASSISTANT_BACKEND_MODE=live`
  - 调真实 Java 后端
- `AI_ASSISTANT_BACKEND_MODE=mock`
  - 使用 Python 本地 stub 结果
  - 适合在 Java 接口未稳定时先跑通 Python agent 编排

当前统一聊天入口：

- `POST /assistant/chat`

当前翻译入口：

- `POST /translation/execute`

请求体：

```json
{
  "learner_id": "learner-1",
  "source_text": "我昨天去了图书馆。",
  "direction": "zh_to_en",
  "stage": "primary_school",
  "user_translation": "I go to library yesterday."
}
```

返回体示例：

```json
{
  "learner_id": "learner-1",
  "direction": "zh_to_en",
  "stage_used": "primary_school",
  "standard_translation": "I went to the library yesterday.",
  "natural_translation": "I went to the library yesterday.",
  "diagnosis_items": [
    {
      "category": "missing_or_mistranslated_content",
      "issue": "译文未准确表达原句含义。",
      "suggestion": "I went to the library yesterday.",
      "explanation": "请先确保核心动作和时间关系与原句一致。"
    }
  ],
  "learning_feedback": [
    "当前方向：zh_to_en",
    "当前学段：小学。反馈时优先保证学生先看懂，再纠正最关键的基础错误。",
    "诊断重点：先看意思是否完整，再看基础语法和固定搭配，不追求复杂表达。",
    "先检查基础语法问题：时态错误。可以先对照 went，再回看原句中的时间关系。",
    "注意固定搭配和词语选择：搭配或冠词使用不当。这类问题通常需要把表达调整为 the library。"
  ],
  "profile_update": {
    "current_stage": "primary_school",
    "preferred_direction": "zh_to_en",
    "direction_counts": {
      "zh_to_en": 1
    }
  }
}
```

说明：

- `stage` 当前支持 `primary_school / junior_high_school / senior_high_school / cet / postgraduate_exam / ielts / toefl`
- 不传 `stage` 时，translation agent 会优先使用 learner 已有画像中的 `current_stage`
- 如果画像中也没有，就默认使用 `senior_high_school`
- 返回里的 `stage_used` 表示这次真正生效的学段策略

请求体：

```json
{
  "message": "Explain present perfect simply",
  "conversation_id": "demo-1",
  "provider": "openai",
  "model": "gpt-5-mini"
}
```

说明：

- `provider` 和 `model` 当前是可选字段
- 传入时，表示本次请求显式使用该模型
- 不传时，使用后端默认 provider 及默认 model
- 当 Redis 状态层可用时，这组选择会按 `conversation_id` 写入会话偏好
- 同一个 `conversation_id` 后续不再显式传 `provider/model` 时，会默认沿用上一次选择

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

错误返回约定：

- provider 不支持：`400`
- 上游模型超时：`504`
- 上游模型返回 HTTP 错误：透传对应状态码，并返回可读 `detail`

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
        "provider": "dashscope",
        "model": "qwen-plus",
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
