# Assistant Provider Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 为 `ai-assistant` 实现默认使用 `Kimi` 的统一聊天 assistant，并保留未来新增 provider 的扩展结构。

**Architecture:** 新增 `/assistant/chat` 统一入口，由 `AssistantService` 调用默认 provider。Provider 通过注册表和协议解耦，第一版只实现 `KimiProvider`，状态写入继续复用 RedisStateStore，LangGraph 暂时保留现状不扩展复杂编排。

**Tech Stack:** Python, FastAPI, httpx, pydantic, pydantic-settings, Redis, pytest

---

### Task 1: Provider 配置与协议

**Files:**
- Create: `app/providers/base.py`
- Create: `app/providers/kimi.py`
- Create: `app/providers/registry.py`
- Modify: `app/core/config.py`
- Test: `tests/test_provider_config.py`

- [ ] **Step 1: Write the failing test**

```python
def test_settings_defaults_provider_to_kimi():
    settings = Settings()
    assert settings.default_provider == "kimi"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.\.venv\Scripts\python.exe -m pytest tests/test_provider_config.py -v`
Expected: FAIL because `default_provider` and kimi config do not exist yet

- [ ] **Step 3: Write minimal implementation**

```python
class Settings(BaseSettings):
    default_provider: str = "kimi"
    kimi_api_key: str = ""
    kimi_base_url: str = "https://api.moonshot.cn/v1"
    kimi_model: str = "moonshot-v1-8k"
```

- [ ] **Step 4: Run test to verify it passes**

Run: `.\.venv\Scripts\python.exe -m pytest tests/test_provider_config.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add app/core/config.py app/providers/base.py app/providers/kimi.py app/providers/registry.py tests/test_provider_config.py
git commit -m "feat(provider): 增加 kimi 默认配置与适配器骨架"
```

### Task 2: Assistant Service

**Files:**
- Create: `app/services/assistant_service.py`
- Modify: `app/core/dependencies.py`
- Test: `tests/test_assistant_service.py`

- [ ] **Step 1: Write the failing test**

```python
@pytest.mark.anyio
async def test_assistant_service_uses_provider_and_persists_state():
    result = await service.chat("hello", conversation_id="c1")
    assert result["reply"] == "hi"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.\.venv\Scripts\python.exe -m pytest tests/test_assistant_service.py -v`
Expected: FAIL because `AssistantService` does not exist yet

- [ ] **Step 3: Write minimal implementation**

```python
class AssistantService:
    async def chat(self, message: str, conversation_id: str | None = None) -> dict[str, object]:
        ...
```

- [ ] **Step 4: Run test to verify it passes**

Run: `.\.venv\Scripts\python.exe -m pytest tests/test_assistant_service.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add app/services/assistant_service.py app/core/dependencies.py tests/test_assistant_service.py
git commit -m "feat(service): 增加统一 assistant service"
```

### Task 3: Assistant 路由

**Files:**
- Modify: `app/api/routes.py`
- Modify: `app/schemas/agent.py`
- Test: `tests/test_assistant_route.py`

- [ ] **Step 1: Write the failing test**

```python
def test_assistant_chat_returns_provider_model_and_reply():
    response = client.post("/assistant/chat", json={"message": "hello"})
    assert response.status_code == 200
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.\.venv\Scripts\python.exe -m pytest tests/test_assistant_route.py -v`
Expected: FAIL because route and schemas do not exist yet

- [ ] **Step 3: Write minimal implementation**

```python
@router.post("/assistant/chat")
async def assistant_chat(...):
    ...
```

- [ ] **Step 4: Run test to verify it passes**

Run: `.\.venv\Scripts\python.exe -m pytest tests/test_assistant_route.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add app/api/routes.py app/schemas/agent.py tests/test_assistant_route.py
git commit -m "feat(api): 增加 assistant chat 接口"
```

### Task 4: 全量回归

**Files:**
- Modify: `README.md`
- Test: `tests/`

- [ ] **Step 1: 更新 README 的启动与环境变量说明**

- [ ] **Step 2: 运行全量测试**

Run: `.\.venv\Scripts\python.exe -m pytest -v`
Expected: PASS

- [ ] **Step 3: Commit**

```bash
git add README.md tests
git commit -m "docs(api): 更新 assistant 接入说明"
```
