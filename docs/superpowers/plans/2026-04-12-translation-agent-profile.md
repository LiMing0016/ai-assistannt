# Translation Agent With Profile Signals Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 为项目落地第一版翻译 agent，并在翻译纠错场景中提取结构化用户信号，更新翻译相关用户画像。

**Architecture:** 采用单 agent workflow。翻译链路负责翻译、纠错、学习反馈；画像链路负责信号提取和画像更新。两者通过结构化 schema 解耦，而不是让 agent 直接操作画像细节。

**Tech Stack:** Python, FastAPI, pydantic, httpx, pytest, Redis

---

### Task 1: 定义翻译与画像 schema

**Files:**
- Create: `app/schemas/translation.py`
- Modify: `app/state/models.py`
- Test: `tests/test_translation_schema.py`

- [ ] **Step 1: Write the failing test**

定义并断言以下模型：

- `TranslationRequest`
- `TranslationResponse`
- `DiagnosisItem`
- `TranslationSignal`
- `TranslationProfileSnapshot`

- [ ] **Step 2: Run test to verify it fails**

Run: `.\.venv\Scripts\python.exe -m pytest tests/test_translation_schema.py -v`
Expected: FAIL because schema files do not exist yet

- [ ] **Step 3: Write minimal implementation**

只实现最小字段：

- 普通翻译字段
- 用户译文字段
- 4 类错误标签
- 画像信号字段

- [ ] **Step 4: Run test to verify it passes**

Run: `.\.venv\Scripts\python.exe -m pytest tests/test_translation_schema.py -v`
Expected: PASS

### Task 2: 扩展 backend client 和 translate tool

**Files:**
- Modify: `app/integrations/backend_client.py`
- Create: `app/tools/translate.py`
- Modify: `app/tools/registry.py`
- Test: `tests/test_translate_tool.py`
- Test: `tests/test_backend_client.py`

- [ ] **Step 1: Write the failing test**

增加：

- `translate_text()` backend client 测试
- `TranslateTool` 调用 backend client 测试

- [ ] **Step 2: Run test to verify it fails**

Run: `.\.venv\Scripts\python.exe -m pytest tests/test_translate_tool.py tests/test_backend_client.py -v`
Expected: FAIL because translate path and tool do not exist yet

- [ ] **Step 3: Write minimal implementation**

新增：

- `AI_ASSISTANT_BACKEND_TRANSLATE_PATH`
- backend translate request/response
- `TranslateTool`
- tool registry 注册翻译工具

- [ ] **Step 4: Run test to verify it passes**

Run: `.\.venv\Scripts\python.exe -m pytest tests/test_translate_tool.py tests/test_backend_client.py -v`
Expected: PASS

### Task 3: 实现 translation signal extractor

**Files:**
- Create: `app/profile/extractor/translation_signal_extractor.py`
- Test: `tests/test_translation_signal_extractor.py`

- [ ] **Step 1: Write the failing test**

测试 extractor 能把翻译诊断结果转成：

- `frequent_error_types`
- `grammar_weak_points`
- `lexical_weak_points`
- `literal_translation_tendency`

- [ ] **Step 2: Run test to verify it fails**

Run: `.\.venv\Scripts\python.exe -m pytest tests/test_translation_signal_extractor.py -v`
Expected: FAIL because extractor does not exist yet

- [ ] **Step 3: Write minimal implementation**

先做纯 Python 映射逻辑，不引入模型推理。

- [ ] **Step 4: Run test to verify it passes**

Run: `.\.venv\Scripts\python.exe -m pytest tests/test_translation_signal_extractor.py -v`
Expected: PASS

### Task 4: 实现翻译画像更新器

**Files:**
- Create: `app/profile/updater/translation_profile_updater.py`
- Modify: `app/state/redis_store.py`
- Test: `tests/test_translation_profile_updater.py`

- [ ] **Step 1: Write the failing test**

测试 updater 能：

- 新建翻译画像
- 累积错误类型计数
- 更新方向偏好
- 合并薄弱点

- [ ] **Step 2: Run test to verify it fails**

Run: `.\.venv\Scripts\python.exe -m pytest tests/test_translation_profile_updater.py -v`
Expected: FAIL because updater and state support do not exist yet

- [ ] **Step 3: Write minimal implementation**

优先实现：

- profile load/save
- 增量更新
- 返回更新后的快照

- [ ] **Step 4: Run test to verify it passes**

Run: `.\.venv\Scripts\python.exe -m pytest tests/test_translation_profile_updater.py -v`
Expected: PASS

### Task 5: 实现 translation agent 服务

**Files:**
- Create: `app/agents/english/translation_agent.py`
- Create: `app/services/translation_service.py`
- Test: `tests/test_translation_agent.py`

- [ ] **Step 1: Write the failing test**

测试两种模式：

- 普通翻译
- 用户提交译文后的纠错模式

并断言响应中包含：

- 翻译结果
- 诊断结果
- 学习反馈
- 画像更新摘要

- [ ] **Step 2: Run test to verify it fails**

Run: `.\.venv\Scripts\python.exe -m pytest tests/test_translation_agent.py -v`
Expected: FAIL because translation agent and service do not exist yet

- [ ] **Step 3: Write minimal implementation**

将以下组件串起来：

- translate tool
- diagnosis builder
- signal extractor
- profile updater

- [ ] **Step 4: Run test to verify it passes**

Run: `.\.venv\Scripts\python.exe -m pytest tests/test_translation_agent.py -v`
Expected: PASS

### Task 6: 暴露翻译 API

**Files:**
- Modify: `app/api/routes.py`
- Modify: `app/core/dependencies.py`
- Test: `tests/test_translation_route.py`

- [ ] **Step 1: Write the failing test**

新增翻译接口测试，覆盖：

- 普通翻译请求
- 带用户译文的纠错请求
- 返回画像更新摘要

- [ ] **Step 2: Run test to verify it fails**

Run: `.\.venv\Scripts\python.exe -m pytest tests/test_translation_route.py -v`
Expected: FAIL because route does not exist yet

- [ ] **Step 3: Write minimal implementation**

新增翻译接口与依赖注入。

- [ ] **Step 4: Run test to verify it passes**

Run: `.\.venv\Scripts\python.exe -m pytest tests/test_translation_route.py -v`
Expected: PASS

### Task 7: 文档与全量回归

**Files:**
- Modify: `.env.example`
- Modify: `README.md`
- Test: `tests/`

- [ ] **Step 1: 更新配置模板**

补充翻译相关 backend path。

- [ ] **Step 2: 更新 README**

说明：

- 翻译接口
- 纠错模式
- 画像更新行为

- [ ] **Step 3: 跑全量测试**

Run: `.\.venv\Scripts\python.exe -m pytest -v`
Expected: PASS
