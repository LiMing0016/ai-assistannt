# AI Assistant Phase 1 Scaffold Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the minimal Python project scaffold for `ai-assistant` so the repository can run a small FastAPI service with a LangGraph-backed orchestration placeholder and tests.

**Architecture:** Keep the first scaffold intentionally narrow. The app should expose a health endpoint and one placeholder agent endpoint, with configuration, schemas, graph orchestration, and tool wiring separated into small files. The code should be production-shaped but behavior-light, so later features can grow without restructuring.

**Tech Stack:** Python, uv, FastAPI, Pydantic v2, LangGraph, pytest, HTTPX

---

## File Structure

- Create: `pyproject.toml`
  - Project metadata, runtime deps, dev deps, pytest config
- Create: `app/main.py`
  - FastAPI app factory and route registration
- Create: `app/api/routes.py`
  - HTTP endpoints
- Create: `app/core/config.py`
  - Environment-backed settings
- Create: `app/schemas/agent.py`
  - Request/response models
- Create: `app/graphs/agent_graph.py`
  - Minimal LangGraph orchestration wrapper
- Create: `app/tools/registry.py`
  - Tool registry placeholder
- Create: `tests/test_health.py`
  - Health endpoint test
- Create: `tests/test_agent_route.py`
  - Placeholder agent endpoint tests
- Modify: `README.md`
  - Add quickstart and structure summary
- Modify: `.gitignore`
  - Keep Python tooling ignores aligned with scaffold

### Task 1: Prepare Git Baseline for Isolated Work

**Files:**
- Modify: `.gitignore`
- Modify: `README.md`
- Existing: `docs/architecture/ai-assistant-overall-design.md`
- Existing: `docs/superpowers/plans/2026-04-10-ai-assistant-bootstrap.md`
- Create: `.worktrees/` (ignored, via git worktree)

- [ ] **Step 1: Verify current repository status**

Run: `git status --short --branch`

Expected: `main` branch with untracked baseline files only.

- [ ] **Step 2: Stage bootstrap baseline**

Run: `git add .gitignore README.md docs`

Expected: baseline docs and repo hygiene files are staged.

- [ ] **Step 3: Create initial bootstrap commit**

Run: `git commit -m "chore(repo): 初始化 ai-assistant 仓库基线"`

Expected: repository has first commit and `main` is clean.

- [ ] **Step 4: Verify `.worktrees/` is ignored**

Run: `git check-ignore -q .worktrees`

Expected: exit code 0.

- [ ] **Step 5: Create isolated worktree branch**

Run: `git worktree add .worktrees/agent-phase1 -b codex/agent-phase1-scaffold`

Expected: isolated workspace created for scaffold work.

### Task 2: Create Project Metadata with TDD Entry Points

**Files:**
- Create: `pyproject.toml`

- [ ] **Step 1: Write the failing health test**

Create `tests/test_health.py` with a `TestClient` request to `/health` expecting `{ "ok": true }`.

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_health.py -v`

Expected: FAIL because app module does not exist yet.

- [ ] **Step 3: Add `pyproject.toml`**

Include minimal project metadata and dependencies:

- runtime: `fastapi`, `uvicorn`, `pydantic`, `langgraph`, `langchain-core`, `httpx`
- dev: `pytest`

- [ ] **Step 4: Verify dependency file exists**

Run: `Get-Content pyproject.toml`

Expected: metadata and dependency groups present.

### Task 3: Build Minimal FastAPI App

**Files:**
- Create: `app/main.py`
- Create: `app/api/routes.py`
- Create: `app/core/config.py`
- Create: `app/schemas/agent.py`

- [ ] **Step 1: Implement the minimal app to satisfy health test**

Add a FastAPI app with `/health`.

- [ ] **Step 2: Run health test to verify it passes**

Run: `pytest tests/test_health.py -v`

Expected: PASS.

- [ ] **Step 3: Write failing placeholder agent route test**

Create `tests/test_agent_route.py` for `POST /agent/execute` with a request body and expected structured response.

- [ ] **Step 4: Run agent route test to verify it fails**

Run: `pytest tests/test_agent_route.py -v`

Expected: FAIL because route is missing.

- [ ] **Step 5: Add schemas, config, and route**

Implement:

- request model with `message`
- response model with `reply`, `trace_id`, `processor`
- placeholder route delegating to graph layer

- [ ] **Step 6: Run route tests**

Run: `pytest tests/test_health.py tests/test_agent_route.py -v`

Expected: both PASS.

### Task 4: Add LangGraph Placeholder and Tool Registry

**Files:**
- Create: `app/graphs/agent_graph.py`
- Create: `app/tools/registry.py`
- Modify: `app/api/routes.py`

- [ ] **Step 1: Write a failing graph integration expectation**

Extend `tests/test_agent_route.py` to assert response includes `processor = "langgraph"` and placeholder reply content from graph execution.

- [ ] **Step 2: Run agent route test to verify it fails**

Run: `pytest tests/test_agent_route.py -v`

Expected: FAIL because the route still uses stubbed inline data.

- [ ] **Step 3: Implement minimal LangGraph wrapper**

Create a tiny graph executor returning a structured placeholder response.

- [ ] **Step 4: Add tool registry placeholder**

Create a registry object or function returning an empty tool set for now.

- [ ] **Step 5: Wire route to graph layer**

Move route behavior out of API layer into graph execution.

- [ ] **Step 6: Run tests**

Run: `pytest tests/test_health.py tests/test_agent_route.py -v`

Expected: PASS.

### Task 5: Document the Scaffold

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Update README with quickstart**

Add:

- project purpose
- basic structure
- recommended first commands

- [ ] **Step 2: Run full current test suite**

Run: `pytest -v`

Expected: all scaffold tests PASS.

- [ ] **Step 3: Review repository status**

Run: `git status --short`

Expected: only intended scaffold files are modified in the worktree.

