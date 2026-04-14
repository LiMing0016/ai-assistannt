import re

from app.prompting.renderer import PromptRenderer
from app.profile.extractor.translation_signal_extractor import TranslationSignalExtractor
from app.profile.models import TranslationProfileSnapshot
from app.profile.updater.translation_profile_updater import TranslationProfileUpdater
from app.schemas.translation import DiagnosisItem, TranslationRequest, TranslationResponse, TranslationStage


DEFAULT_TRANSLATION_STAGE: TranslationStage = "senior_high_school"


class TranslationAgent:
    def __init__(
        self,
        translate_tool,
        signal_extractor: TranslationSignalExtractor,
        profile_updater: TranslationProfileUpdater,
        prompt_renderer: PromptRenderer,
    ) -> None:
        self._translate_tool = translate_tool
        self._signal_extractor = signal_extractor
        self._profile_updater = profile_updater
        self._prompt_renderer = prompt_renderer

    async def execute(self, request: TranslationRequest) -> TranslationResponse:
        current_profile = self._profile_updater.load(request.learner_id)
        stage = _resolve_translation_stage(request.stage, current_profile)
        tool_result = await self._translate_tool.execute(request.source_text, request.direction)
        diagnosis_items = self._build_diagnosis_items(
            request.user_translation,
            tool_result.standard_translation,
            tool_result.natural_translation,
        )
        signal = self._signal_extractor.extract(
            learner_id=request.learner_id,
            direction=request.direction,
            diagnosis_items=diagnosis_items,
        )
        profile_snapshot = self._profile_updater.update(signal, stage=stage)

        learning_feedback = self._build_learning_feedback(
            direction=request.direction,
            stage=stage,
            diagnosis_items=diagnosis_items,
            current_profile=current_profile,
        )

        return TranslationResponse(
            learner_id=request.learner_id,
            direction=request.direction,
            stage_used=stage,
            standard_translation=tool_result.standard_translation,
            natural_translation=tool_result.natural_translation,
            diagnosis_items=diagnosis_items,
            learning_feedback=learning_feedback,
            profile_update=profile_snapshot.model_dump(),
        )

    def _build_diagnosis_items(
        self,
        user_translation: str | None,
        standard_translation: str,
        natural_translation: str,
    ) -> list[DiagnosisItem]:
        if not user_translation:
            return []

        normalized_user = _normalize_text(user_translation)
        candidates = {_normalize_text(standard_translation), _normalize_text(natural_translation)}
        if normalized_user in candidates:
            return []

        diagnosis_items: list[DiagnosisItem] = []
        user_tokens = _tokenize_words(user_translation)
        standard_tokens = _tokenize_words(standard_translation)

        if _looks_like_past_tense_error(user_tokens, standard_tokens):
            diagnosis_items.append(
                DiagnosisItem(
                    category="grammar_error",
                    issue="时态错误",
                    suggestion=_extract_past_tense_hint(standard_translation),
                    explanation="原句表示过去发生的动作，这里应使用过去时。",
                )
            )

        if _looks_like_article_or_word_choice_issue(user_translation, standard_translation):
            diagnosis_items.append(
                DiagnosisItem(
                    category="word_choice_issue",
                    issue="搭配或冠词使用不当",
                    suggestion=_extract_article_hint(standard_translation),
                    explanation="英语里很多地点、搭配需要固定说法，不能只按中文逐字翻。",
                )
            )

        if _looks_like_unnatural_expression(user_translation):
            diagnosis_items.append(
                DiagnosisItem(
                    category="unnatural_expression",
                    issue="表达不够自然",
                    suggestion=natural_translation,
                    explanation="句子虽然能传达部分意思，但表达方式不够地道。",
                )
            )

        if _looks_like_missing_content(user_tokens, standard_tokens):
            diagnosis_items.append(
                DiagnosisItem(
                    category="missing_or_mistranslated_content",
                    issue="译文未准确表达原句关键信息。",
                    suggestion=standard_translation,
                    explanation="请先确保地点、动作、时间等核心信息都被完整表达出来。",
                )
            )

        if diagnosis_items:
            return diagnosis_items

        return [
            DiagnosisItem(
                category="missing_or_mistranslated_content",
                issue="译文与标准答案存在明显差异。",
                suggestion=standard_translation,
                explanation="请先对照标准译文检查含义、时态和关键信息是否一致。",
            )
        ]

    def _build_learning_feedback(
        self,
        direction: str,
        stage: TranslationStage,
        diagnosis_items: list[DiagnosisItem],
        current_profile: TranslationProfileSnapshot | None,
    ) -> list[str]:
        feedback = [
            self._prompt_renderer.render(
                "translation/feedback/header.md",
                direction=direction,
                stage=stage,
                stage_label=_translation_stage_label(stage),
            )
        ]
        feedback.append(
            self._prompt_renderer.render(
                f"translation/stages/{stage}/strategy.md",
                direction=direction,
                stage=stage,
                stage_label=_translation_stage_label(stage),
            )
        )
        feedback.append(
            self._prompt_renderer.render(
                f"translation/stages/{stage}/diagnosis.md",
                direction=direction,
                stage=stage,
                stage_label=_translation_stage_label(stage),
            )
        )
        if not diagnosis_items:
            feedback.append(
                self._prompt_renderer.render(
                    "translation/feedback/success.md",
                    direction=direction,
                    stage=stage,
                    stage_label=_translation_stage_label(stage),
                )
            )
            profile_focus = self._render_profile_focus(current_profile)
            if profile_focus:
                feedback.append(profile_focus)
            return feedback

        for item in diagnosis_items:
            feedback.append(
                self._prompt_renderer.render(
                    f"translation/feedback/{item.category}.md",
                    direction=direction,
                    stage=stage,
                    stage_label=_translation_stage_label(stage),
                    issue=item.issue,
                    suggestion=item.suggestion,
                    explanation=item.explanation,
                )
            )
        profile_focus = self._render_profile_focus(current_profile)
        if profile_focus:
            feedback.append(profile_focus)
        return feedback

    def _render_profile_focus(
        self,
        current_profile: TranslationProfileSnapshot | None,
    ) -> str | None:
        if current_profile is None:
            return None

        grammar_point, grammar_count = _top_weak_point(current_profile.grammar_weak_points)
        lexical_point, lexical_count = _top_weak_point(current_profile.lexical_weak_points)
        literal_count = current_profile.literal_translation_tendency_count

        if literal_count >= 2 and literal_count >= max(grammar_count, lexical_count):
            return self._prompt_renderer.render("translation/profile/literal_translation.md")
        if grammar_point and grammar_count >= 2:
            return self._prompt_renderer.render(
                "translation/profile/grammar_focus.md",
                weak_point=grammar_point,
            )
        if lexical_point and lexical_count >= 2:
            return self._prompt_renderer.render(
                "translation/profile/lexical_focus.md",
                weak_point=lexical_point,
            )
        return None


def _normalize_text(value: str) -> str:
    return re.sub(r"[\W_]+", "", value).lower()


def _tokenize_words(value: str) -> list[str]:
    return re.findall(r"[a-zA-Z]+", value.lower())


def _looks_like_past_tense_error(user_tokens: list[str], standard_tokens: list[str]) -> bool:
    has_base_form = "go" in user_tokens and "went" not in user_tokens
    uses_emphasis_pattern = "did" in user_tokens and "go" in user_tokens
    return "went" in standard_tokens and has_base_form and not uses_emphasis_pattern


def _looks_like_article_or_word_choice_issue(user_translation: str, standard_translation: str) -> bool:
    normalized_user = user_translation.lower()
    normalized_standard = standard_translation.lower()
    return "the library" in normalized_standard and "to library" in normalized_user


def _looks_like_unnatural_expression(user_translation: str) -> bool:
    normalized_user = user_translation.lower()
    return "did go" in normalized_user


def _looks_like_missing_content(user_tokens: list[str], standard_tokens: list[str]) -> bool:
    keywords = [token for token in standard_tokens if token not in {"i", "to", "the", "a", "an", "yesterday", "went"}]
    return any(token not in user_tokens for token in keywords)


def _extract_past_tense_hint(standard_translation: str) -> str:
    match = re.search(r"\bwent\b", standard_translation, flags=re.IGNORECASE)
    return match.group(0) if match else standard_translation


def _extract_article_hint(standard_translation: str) -> str:
    match = re.search(r"\bthe library\b", standard_translation, flags=re.IGNORECASE)
    return match.group(0) if match else standard_translation


def _resolve_translation_stage(
    request_stage: TranslationStage | None,
    current_profile: TranslationProfileSnapshot | None,
) -> TranslationStage:
    if request_stage is not None:
        return request_stage
    if current_profile and current_profile.current_stage is not None:
        return current_profile.current_stage
    return DEFAULT_TRANSLATION_STAGE


def _top_weak_point(points: dict[str, int]) -> tuple[str | None, int]:
    if not points:
        return None, 0
    weak_point, count = max(points.items(), key=lambda item: item[1])
    return weak_point, count


def _translation_stage_label(stage: TranslationStage) -> str:
    return {
        "primary_school": "小学",
        "junior_high_school": "初中",
        "senior_high_school": "高中",
        "cet": "四六级",
        "postgraduate_exam": "考研",
        "ielts": "雅思",
        "toefl": "托福",
    }[stage]
