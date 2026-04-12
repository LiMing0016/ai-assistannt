# Agent 平台目录与阶段规划

## 1. 采用方案

本项目采用：

`方案一：重平台先行，但按阶段实施`

这意味着：

- 目录结构按平台终局方向设计
- 实际能力按阶段逐步填充
- 允许部分目录在当前阶段仅作为骨架存在
- 不要求一次性实现所有 planner / memory / skill / workflow 能力

---

## 2. 当前推荐目录

```text
app/
├─ api/
├─ core/
├─ platform/
│  ├─ orchestrator/
│  ├─ planner/
│  ├─ registry/
│  ├─ router/
│  └─ runtime/
├─ agents/
│  ├─ english/
│  └─ shared/
├─ tools/
│  ├─ english/
│  └─ shared/
├─ providers/
├─ profile/
│  ├─ extractor/
│  ├─ evaluator/
│  ├─ updater/
│  └─ models.py
├─ memory/
├─ state/
├─ integrations/
├─ observability/
├─ schemas/
└─ services/
```

---

## 3. 各层职责

### `platform/`

平台公共内核，不直接耦合英语业务。

- `orchestrator/`：多步执行编排
- `planner/`：任务拆解与步骤规划
- `registry/`：provider / tool / agent 注册
- `router/`：请求分发与能力路由
- `runtime/`：运行上下文、trace、checkpoint

### `agents/`

领域 Agent 定义层。

- `english/`：英语领域 agent
- `shared/`：通用 agent 组件

### `tools/`

能力执行层。

- `english/`：讲解、翻译、润色、改写、知识图谱
- `shared/`：通用工具

### `profile/`

用户理解与能力画像层。

- `extractor/`：提取对话和行为信号
- `evaluator/`：评估能力水平
- `updater/`：更新画像

### `memory/`

学习记忆与可检索上下文。

### `state/`

偏运行态：

- Redis
- task state
- queue state
- conversation state

---

## 4. 阶段规划

### Phase 1：平台骨架可运行

必须完成：

- `providers`
- `services`
- `/assistant/chat`
- `platform/runtime`
- `platform/registry`
- `state`
- `observability`

当前默认 provider：

- `kimi`

### Phase 2：英语领域能力接入

必须完成：

- `agents/english`
- `tools/english`
- explain / translate / polish / rewrite
- english routing

### Phase 3：能力画像闭环

必须完成：

- `profile/models.py`
- `profile/extractor`
- `profile/evaluator`
- `profile/updater`
- `memory`

### Phase 4：平台增强

必须完成：

- `platform/orchestrator`
- `platform/planner`
- 异步长任务
- 知识图谱流程
- 多学科扩展准备

---

## 5. 迁移原则

当前已有代码不强制一次性迁移。

迁移顺序建议：

1. 先补新目录骨架
2. 再把新功能优先写入新目录
3. 旧目录中的早期实现按需逐步迁移
4. 每次迁移都保证测试仍可通过

---

## 6. 当前结论

本项目已经从“单助手工程”转向“领域型 Agent 平台工程”。

英语是第一领域，不是唯一领域。

因此：

- 目录结构应先按平台设计
- 功能实现按阶段推进
- 用户理解与能力画像必须作为平台主线之一保留
