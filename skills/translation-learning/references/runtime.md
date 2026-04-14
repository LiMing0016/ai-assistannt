# Skill Routing

- 先把请求分成 `direct_translation`、`translation_diagnosis`、`clarification_needed`
- 直接翻译请求：优先给结果，说明从简
- 批改诊断请求：先给正确版本，再给问题，再给学习反馈
- 信息不够时：只问一个最小澄清问题，不做高风险猜测

## Translation Output

- 始终优先保证准确、自然、符合语境
- 默认产出 `standard_translation`
- 需要时补 `natural_translation`
- 不把译文结果和评论混在一段里

## Diagnosis Rules

- 优先指出影响理解和正确性的主要问题
- 标签顺序优先为：
  1. `missing_or_mistranslated_content`
  2. `grammar_error`
  3. `word_choice_issue`
  4. `unnatural_expression`
- 不为了让反馈显得丰富而制造问题

## Stage Usage

- 如果后端已提供用户 `stage`，再加载对应 stage 文件
- stage 只调整反馈深度、术语密度、关注重点和建议语气
- stage 不应改变翻译本身的正确性
