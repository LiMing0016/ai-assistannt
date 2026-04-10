# AI Assistant Bootstrap Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Initialize `F:\ai-assistant` as a clean Git-based Python agent orchestration project with baseline repository hygiene and a minimal starting structure for Phase 1.

**Architecture:** Keep the repository bootstrap intentionally small: establish version control, ignore generated files, preserve the architecture design doc, and prepare the project for a FastAPI + LangGraph implementation without prematurely locking runtime details. This plan only covers repository setup and bootstrap hygiene, not the full agent runtime.

**Tech Stack:** Git, Markdown docs, Python project conventions

---

## File Structure

- Existing: `docs/architecture/ai-assistant-overall-design.md`
  - Repository architecture baseline and future-state design
- Create: `.gitignore`
  - Ignore local tooling, Python caches, virtual environments, coverage output, and brainstorm artifacts
- Create: `README.md`
  - Minimal repo entry point with project purpose and links to architecture docs
- Existing/Create: `docs/superpowers/plans/2026-04-10-ai-assistant-bootstrap.md`
  - Bootstrap execution plan

### Task 1: Initialize Repository

**Files:**
- Create: `.git/` (via `git init`)

- [ ] **Step 1: Verify current workspace state**

Run: `Get-ChildItem -Force F:\ai-assistant`

Expected: only docs and local working directories are present, and `.git` does not exist.

- [ ] **Step 2: Initialize Git repository on main branch**

Run: `git init -b main`

Expected: Git repository created in `F:\ai-assistant\.git`.

- [ ] **Step 3: Verify repository initialized**

Run: `git status --short --branch`

Expected: branch shows `main` and current files are untracked.

### Task 2: Add Baseline Repository Hygiene

**Files:**
- Create: `.gitignore`
- Create: `README.md`

- [ ] **Step 1: Add `.gitignore`**

Include:

```gitignore
.superpowers/
.venv/
venv/
__pycache__/
.pytest_cache/
.mypy_cache/
.ruff_cache/
.coverage
htmlcov/
dist/
build/
.env
```

- [ ] **Step 2: Add minimal `README.md`**

Include:

```md
# ai-assistant

独立的 Python Agent 编排层工程，用于为 `personalenglishai` 提供 AI Agent 能力。

当前总体设计见：

- `docs/architecture/ai-assistant-overall-design.md`
```

- [ ] **Step 3: Verify Git sees only intended files**

Run: `git status --short`

Expected: `.gitignore`, `README.md`, and `docs/` are shown; `.superpowers/` is ignored.

### Task 3: Hand Off to Phase 1 Scaffold

**Files:**
- Future plan: `docs/superpowers/plans/<phase-1-plan>.md`

- [ ] **Step 1: Confirm bootstrap is complete**

Check:

- Git repository exists
- `.gitignore` is active
- architecture document is preserved
- repository root is ready for Python scaffold

- [ ] **Step 2: Create the next implementation plan**

The next plan should cover:

- Python dependency management choice
- FastAPI app layout
- LangGraph orchestration skeleton
- Redis and LangSmith configuration boundaries
- Initial test strategy

