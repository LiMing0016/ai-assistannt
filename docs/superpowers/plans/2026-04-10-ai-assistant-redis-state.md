# AI Assistant Redis State Foundation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add conversation state and task state models to the Redis layer so the current scaffold has a stable foundation for future synchronous memory handling and asynchronous task execution.

**Architecture:** Keep Redis integration shallow but explicit. Add typed state models, serialization helpers, and a storage interface that can be used locally without a running Redis server by injecting a fake client in tests. Do not implement worker orchestration yet; only persist and retrieve state.

**Tech Stack:** Python, Pydantic v2, Redis, pytest

---

## File Structure

- Create: `app/state/models.py`
  - Conversation and task state DTOs
- Modify: `app/state/redis_store.py`
  - Add typed read/write methods and graceful fallback
- Create: `tests/test_redis_store.py`
  - State layer tests using fake Redis client
- Modify: `app/graphs/agent_graph.py`
  - Save conversation append and expose task foundation metadata
- Modify: `app/schemas/agent.py`
  - Add state metadata to response
- Modify: `tests/test_agent_route.py`
  - Verify state metadata fields

### Task 1: Define State Models

**Files:**
- Create: `app/state/models.py`
- Create: `tests/test_redis_store.py`

- [ ] **Step 1: Write failing state model/store test**

Test should assert:

- conversation messages can be appended and re-read
- task state can be stored and read by task id

- [ ] **Step 2: Run test to verify it fails**

Run: `.\.venv\Scripts\python.exe -m pytest tests/test_redis_store.py -v`

Expected: FAIL because state models and store methods do not exist.

- [ ] **Step 3: Implement typed state models**

Include:

- `ConversationMessage`
- `ConversationState`
- `TaskState`

### Task 2: Extend Redis Store

**Files:**
- Modify: `app/state/redis_store.py`
- Modify: `tests/test_redis_store.py`

- [ ] **Step 1: Add serialization helpers**

Support:

- conversation append
- conversation load
- task save
- task load

- [ ] **Step 2: Keep Redis optional**

The store should still expose `is_enabled()` and remain testable with injected fake client.

- [ ] **Step 3: Run state tests**

Run: `.\.venv\Scripts\python.exe -m pytest tests/test_redis_store.py -v`

Expected: PASS.

### Task 3: Surface State Metadata Through Agent Route

**Files:**
- Modify: `app/graphs/agent_graph.py`
- Modify: `app/schemas/agent.py`
- Modify: `tests/test_agent_route.py`

- [ ] **Step 1: Extend route test with state metadata expectation**

Assert response includes:

- `state.conversation_enabled`
- `state.task_state_enabled`

- [ ] **Step 2: Run route test to verify it fails**

Run: `.\.venv\Scripts\python.exe -m pytest tests/test_agent_route.py -v`

Expected: FAIL because metadata is missing.

- [ ] **Step 3: Update graph response**

Expose state metadata derived from the Redis store.

- [ ] **Step 4: Run route test**

Run: `.\.venv\Scripts\python.exe -m pytest tests/test_agent_route.py -v`

Expected: PASS.

### Task 4: Final Verification

**Files:**
- Modify: `README.md` only if state layer setup needs documentation

- [ ] **Step 1: Run full test suite**

Run: `.\.venv\Scripts\python.exe -m pytest -v`

Expected: all tests PASS.

- [ ] **Step 2: Review worktree status**

Run: `git status --short`

Expected: only intended files are modified.

