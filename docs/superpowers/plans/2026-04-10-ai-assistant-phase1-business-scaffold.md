# AI Assistant Phase 1 Business Scaffold Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Extend the current Phase 1 scaffold with production-shaped boundaries for configuration, Java backend HTTP integration, Redis state access, LangSmith toggling, and a first real tool contract.

**Architecture:** Keep the runtime small but structured. Configuration should be centralized, outbound integrations should be isolated behind focused modules, and the first tool should flow through the graph layer instead of being hardcoded in the route. External systems remain optional via configuration so tests can stay local and deterministic.

**Tech Stack:** Python, FastAPI, Pydantic v2, LangGraph, HTTPX, Redis, pytest

---

## File Structure

- Modify: `pyproject.toml`
  - Add runtime dependency for Redis
- Modify: `app/core/config.py`
  - Add environment-backed settings for backend, Redis, and LangSmith toggle
- Create: `app/core/dependencies.py`
  - Dependency wiring for settings, client, state store, and graph service
- Create: `app/integrations/backend_client.py`
  - Java backend HTTP client abstraction
- Create: `app/state/redis_store.py`
  - Redis-backed state store abstraction with graceful disable mode
- Create: `app/observability/langsmith.py`
  - LangSmith toggle and trace metadata helper
- Modify: `app/graphs/agent_graph.py`
  - Route graph execution through first real tool
- Create: `app/tools/explain.py`
  - First real tool contract for explanation
- Modify: `app/tools/registry.py`
  - Register explain tool
- Modify: `app/schemas/agent.py`
  - Carry tool and metadata in response
- Modify: `app/api/routes.py`
  - Use dependency wiring instead of inline construction
- Create: `tests/test_config.py`
  - Settings tests
- Create: `tests/test_explain_tool.py`
  - Explain tool tests
- Modify: `tests/test_agent_route.py`
  - Route integration tests with dependency overrides

### Task 1: Add Integration Dependencies

**Files:**
- Modify: `pyproject.toml`

- [ ] **Step 1: Write the failing settings test**

Create `tests/test_config.py` to assert default settings include backend base URL, Redis URL, and LangSmith toggle fields.

- [ ] **Step 2: Run test to verify it fails**

Run: `.\.venv\Scripts\python.exe -m pytest tests/test_config.py -v`

Expected: FAIL because settings fields do not exist yet.

- [ ] **Step 3: Add Redis dependency**

Add `redis` to runtime dependencies in `pyproject.toml`.

- [ ] **Step 4: Install new dependency**

Run: `.\.venv\Scripts\python.exe -m pip install redis`

Expected: package installs successfully.

### Task 2: Expand Configuration and Dependency Wiring

**Files:**
- Modify: `app/core/config.py`
- Create: `app/core/dependencies.py`
- Create: `tests/test_config.py`

- [ ] **Step 1: Implement settings defaults**

Add fields:

- `backend_base_url`
- `backend_timeout_seconds`
- `redis_url`
- `langsmith_enabled`
- `langsmith_project`

- [ ] **Step 2: Add dependency helpers**

Provide dependency constructors for:

- settings
- backend client
- state store

- [ ] **Step 3: Run config tests**

Run: `.\.venv\Scripts\python.exe -m pytest tests/test_config.py -v`

Expected: PASS.

### Task 3: Add Java Backend Client Abstraction

**Files:**
- Create: `app/integrations/backend_client.py`
- Create: `tests/test_explain_tool.py`

- [ ] **Step 1: Write the failing explain tool test**

Create `tests/test_explain_tool.py` asserting the tool uses a backend client and returns structured output for explanation requests.

- [ ] **Step 2: Run test to verify it fails**

Run: `.\.venv\Scripts\python.exe -m pytest tests/test_explain_tool.py -v`

Expected: FAIL because explain tool and backend client do not exist.

- [ ] **Step 3: Implement backend client protocol**

Add:

- request model for explanation payload
- client class with async method for explanation calls
- configurable base URL and timeout

- [ ] **Step 4: Keep tests local**

Use a fake client in tests; no real network call.

### Task 4: Add Redis State Store and LangSmith Toggle

**Files:**
- Create: `app/state/redis_store.py`
- Create: `app/observability/langsmith.py`
- Modify: `app/core/dependencies.py`

- [ ] **Step 1: Write the failing route integration expectation**

Extend `tests/test_agent_route.py` to assert response metadata includes:

- `tool = "explain_english_knowledge"`
- `tracing.langsmith_enabled`

- [ ] **Step 2: Run route test to verify it fails**

Run: `.\.venv\Scripts\python.exe -m pytest tests/test_agent_route.py -v`

Expected: FAIL because metadata is missing.

- [ ] **Step 3: Add Redis store abstraction**

Implement a class that:

- can be disabled if Redis is unavailable
- exposes `is_enabled()`
- prepares future hooks for conversation/task state

- [ ] **Step 4: Add LangSmith helper**

Implement a small helper returning trace metadata based on settings toggle.

### Task 5: Implement First Real Tool Through the Graph

**Files:**
- Create: `app/tools/explain.py`
- Modify: `app/tools/registry.py`
- Modify: `app/graphs/agent_graph.py`
- Modify: `app/schemas/agent.py`
- Modify: `app/api/routes.py`
- Modify: `tests/test_agent_route.py`
- Modify: `tests/test_explain_tool.py`

- [ ] **Step 1: Implement explain tool**

Tool name:

- `explain_english_knowledge`

Behavior:

- accept user message
- delegate to backend client abstraction
- return structured tool result

- [ ] **Step 2: Register tool**

Return a named registry mapping for future routing.

- [ ] **Step 3: Update graph execution**

Graph should call the explain tool via the registry and return:

- `reply`
- `processor`
- `tool`
- `trace_id`
- `tracing`

- [ ] **Step 4: Update API schema and route**

Keep the route thin; dependency injection should provide graph service dependencies.

- [ ] **Step 5: Run focused tests**

Run: `.\.venv\Scripts\python.exe -m pytest tests/test_explain_tool.py tests/test_agent_route.py -v`

Expected: PASS.

### Task 6: Final Verification

**Files:**
- Modify: `README.md` if setup instructions change

- [ ] **Step 1: Update README if necessary**

Document Redis dependency and environment variables only if reflected in current scaffold.

- [ ] **Step 2: Run full test suite**

Run: `.\.venv\Scripts\python.exe -m pytest -v`

Expected: all tests PASS.

- [ ] **Step 3: Review worktree status**

Run: `git status --short`

Expected: only intended scaffold files are modified.

