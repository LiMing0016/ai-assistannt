# Multi-Provider Session Model Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 为 `ai-assistant` 增加 `OpenAI / Kimi / DashScope` 多 provider 能力，并为会话级模型切换预留请求协议。

**Architecture:** 新增一个公共的 OpenAI-compatible provider 层，复用三家模型厂商的 `chat/completions` 请求流程。`AssistantService` 和 `/assistant/chat` 扩展可选的 `provider/model` 参数，当前先支持请求级覆盖，后续再衔接 conversation state。

**Tech Stack:** Python, FastAPI, httpx, pydantic, pydantic-settings, pytest

---

### Task 1: 配置与 provider registry 扩展

**Files:**
- Modify: `app/core/config.py`
- Modify: `app/providers/registry.py`
- Test: `tests/test_provider_config.py`

- [ ] **Step 1: Write the failing test**

增加以下断言：

- `Settings` 包含 `openai_timeout_seconds`
- `Settings` 包含 `dashscope_timeout_seconds`
- `get_provider()` 能返回 `OpenAIProvider`
- `get_provider()` 能返回 `DashScopeProvider`

- [ ] **Step 2: Run test to verify it fails**

Run: `.\.venv\Scripts\python.exe -m pytest tests/test_provider_config.py -v`
Expected: FAIL because config fields and provider types do not exist yet

- [ ] **Step 3: Write minimal implementation**

补充配置字段，并让 registry 支持：

- `kimi`
- `openai`
- `dashscope`

- [ ] **Step 4: Run test to verify it passes**

Run: `.\.venv\Scripts\python.exe -m pytest tests/test_provider_config.py -v`
Expected: PASS

### Task 2: 抽公共 OpenAI-compatible provider 基类

**Files:**
- Create: `app/providers/openai_compatible.py`
- Create: `app/providers/openai.py`
- Create: `app/providers/dashscope.py`
- Modify: `app/providers/kimi.py`
- Test: `tests/test_provider_config.py`

- [ ] **Step 1: Write the failing test**

增加 provider 响应解析测试：

- `OpenAIProvider` 可解析标准响应
- `DashScopeProvider` 可解析标准响应
- `KimiProvider` 继续通过旧测试

- [ ] **Step 2: Run test to verify it fails**

Run: `.\.venv\Scripts\python.exe -m pytest tests/test_provider_config.py -v`
Expected: FAIL because provider classes do not exist yet

- [ ] **Step 3: Write minimal implementation**

实现公共基类，封装：

- base URL
- Authorization header
- timeout
- model override
- response parsing

- [ ] **Step 4: Run test to verify it passes**

Run: `.\.venv\Scripts\python.exe -m pytest tests/test_provider_config.py -v`
Expected: PASS

### Task 3: assistant service 支持请求级 provider/model 覆盖

**Files:**
- Modify: `app/services/assistant_service.py`
- Test: `tests/test_assistant_service.py`

- [ ] **Step 1: Write the failing test**

增加两个用例：

- 显式传入 `provider/model` 时，使用覆盖值
- 未传入时，使用默认 provider 配置

- [ ] **Step 2: Run test to verify it fails**

Run: `.\.venv\Scripts\python.exe -m pytest tests/test_assistant_service.py -v`
Expected: FAIL because service does not accept override parameters yet

- [ ] **Step 3: Write minimal implementation**

给 `AssistantService.chat()` 增加可选参数：

- `provider`
- `model`

并把解析后的选择传给 provider 层。

- [ ] **Step 4: Run test to verify it passes**

Run: `.\.venv\Scripts\python.exe -m pytest tests/test_assistant_service.py -v`
Expected: PASS

### Task 4: 扩展 `/assistant/chat` 请求协议

**Files:**
- Modify: `app/schemas/agent.py`
- Modify: `app/api/routes.py`
- Test: `tests/test_assistant_route.py`

- [ ] **Step 1: Write the failing test**

增加路由测试：

- 请求体可携带 `provider`
- 请求体可携带 `model`
- 返回结构不变

- [ ] **Step 2: Run test to verify it fails**

Run: `.\.venv\Scripts\python.exe -m pytest tests/test_assistant_route.py -v`
Expected: FAIL because schema does not accept the new fields yet

- [ ] **Step 3: Write minimal implementation**

扩展请求 schema 和路由调用参数透传。

- [ ] **Step 4: Run test to verify it passes**

Run: `.\.venv\Scripts\python.exe -m pytest tests/test_assistant_route.py -v`
Expected: PASS

### Task 5: 文档与回归

**Files:**
- Modify: `.env.example`
- Modify: `README.md`
- Test: `tests/`

- [ ] **Step 1: 更新环境变量模板**

增加：

- `AI_ASSISTANT_OPENAI_TIMEOUT_SECONDS`
- `AI_ASSISTANT_DASHSCOPE_TIMEOUT_SECONDS`

- [ ] **Step 2: 更新 README**

补充：

- 多 provider 配置说明
- `provider/model` 请求字段说明
- 当前“请求级覆盖，后续会接会话级持久化”的说明

- [ ] **Step 3: 跑全量测试**

Run: `.\.venv\Scripts\python.exe -m pytest -v`
Expected: PASS
