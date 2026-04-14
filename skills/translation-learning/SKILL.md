---
name: translation-learning
description: Use when handling English-learning translation requests that may involve direct translation, translation diagnosis, or learning-oriented feedback across zh_to_en and en_to_zh directions.
---

# Translation Learning

## 概述

处理英语学习场景下的翻译请求。

这个 skill 面向自然语言形式的用户请求，不要求上游一定先把请求结构化。它的目标不只是产出译文，还要先判断用户当前更需要的是：

- 直接翻译
- 译文批改诊断
- 信息澄清

然后再给出适合英语学习场景的输出结果。

## 核心分流

收到请求后，先把任务归入以下三类之一：

1. `direct_translation`
   用户主要是要翻译结果，没有提供自己的译文尝试。

2. `translation_diagnosis`
   用户提供了原文，同时也提供了自己的译文，或者明确在问“我这样翻对不对”“这样写行不行”“请帮我改一下”。

3. `clarification_needed`
   当前请求不足以可靠判断原文、翻译方向，或无法区分哪一段是原文、哪一段是用户自己的译文。

不要把单纯的翻译请求强行当成批改请求。
不要把明显的批改请求降级成只给译文。
当原文和用户译文无法可靠区分时，不要硬猜。

## 输入理解

这个 skill 主要处理自然语言请求。

在理解请求时，尽量识别或推断以下信息：

- 原文 `source_text`
- 翻译方向：`zh_to_en` 或 `en_to_zh`
- 用户自己的译文尝试 `user_translation`
- 用户当前真正想要的结果：
  - 只要译文
  - 译文加说明
  - 批改诊断
  - 学习反馈

如果关键信息不明确，先问一个最小澄清问题，不要直接做高风险猜测。

更详细的抽取和澄清规则，见 [references/workflow.md](references/workflow.md)。

## 输出目标

无论是哪种场景，优先产出：

- `standard_translation`
- `natural_translation`

如果当前请求属于批改诊断，再补充：

- `diagnosis_items`
- `learning_feedback`

这个 skill 的目标是兼顾翻译质量和学习价值，而不是只追求把句子机械翻过去。

输出结构和组织方式，见 [references/output-patterns.md](references/output-patterns.md)。

## 诊断原则

当用户提供自己的译文时，尽量识别主要问题，并按优先级组织反馈。

优先级建议如下：

1. 含义遗漏、误译、关键信息不一致
2. 明显语法错误
3. 词语选择、搭配、冠词等问题
4. 表达不自然

不要为了让反馈看起来更丰富而编造问题。
不要把纯风格差异都当成错误。
标签使用要尽量稳定、一致。

诊断标签定义见 [references/diagnosis-labels.md](references/diagnosis-labels.md)。

## 学段适配

如果请求里包含学习阶段 `stage`，应根据阶段调整反馈方式，包括：

- 解释深度
- 术语密度
- 关注重点
- 建议语气

当前支持的阶段包括：

- `primary_school`
- `junior_high_school`
- `senior_high_school`
- `cet`
- `ielts`
- `toefl`
- `postgraduate_exam`

学段策略只用于调整教学反馈方式，不应影响翻译本身的正确性。

具体规则见 [references/stages/](references/stages/) 下对应文件。

## 默认行为

当用户只要求翻译时：

- 直接给出译文
- 默认解释简短
- 只有在确实有价值时，再补充更自然表达或一句简短说明

当用户在问“我这样翻对不对”时：

- 先给正确版本
- 再指出问题
- 最后给学习反馈

当请求信息不足时：

- 先追问一个最小问题
- 不要在高不确定性下强行输出

## 不要这样做

- 不要默认所有翻译请求都是批改请求
- 不要要求用户必须先提供结构化字段
- 不要对简单翻译请求过度讲解
- 不要对批改请求讲得太轻，导致没有学习价值
- 不要把正确译文、自然表达、问题说明和反馈混在一起，导致用户分不清结果和解释
