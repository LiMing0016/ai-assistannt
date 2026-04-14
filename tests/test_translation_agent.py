import asyncio

from app.agents.english.translation_agent import TranslationAgent
from app.core.config import Settings
from app.prompting.loader import PromptLoader
from app.prompting.renderer import PromptRenderer
from app.profile.extractor.translation_signal_extractor import TranslationSignalExtractor
from app.profile.models import TranslationProfileSnapshot
from app.profile.updater.translation_profile_updater import TranslationProfileUpdater
from app.schemas.translation import TranslationRequest


class FakeTranslateTool:
    async def execute(self, source_text: str, direction: str):
        assert source_text == "我昨天去了图书馆。"
        assert direction == "zh_to_en"
        return type(
            "TranslateResult",
            (),
            {
                "tool": "translate_text",
                "standard_translation": "I went to the library yesterday.",
                "natural_translation": "I went to the library yesterday.",
            },
        )()


class FakeTranslationProfileUpdater:
    def __init__(self, current_profile: TranslationProfileSnapshot | None = None) -> None:
        self.current_profile = current_profile

    def load(self, learner_id: str) -> TranslationProfileSnapshot | None:
        if self.current_profile and self.current_profile.learner_id == learner_id:
            return self.current_profile
        return None

    def update(self, signal, stage=None):
        return TranslationProfileSnapshot(
            learner_id=signal.learner_id,
            current_stage=stage or (self.current_profile.current_stage if self.current_profile else None),
            preferred_direction=signal.direction,
            direction_counts={signal.direction: 1},
            frequent_error_types={error_type: 1 for error_type in signal.error_types},
            grammar_weak_points={point: 1 for point in signal.grammar_weak_points},
            lexical_weak_points={point: 1 for point in signal.lexical_weak_points},
            literal_translation_tendency_count=1 if signal.literal_translation_tendency else 0,
        )


def build_project_prompt_renderer() -> PromptRenderer:
    settings = Settings(_env_file=None)
    return PromptRenderer(PromptLoader(base_dir=settings.prompt_base_dir))


def test_translation_agent_returns_translation_feedback_and_profile_update() -> None:
    agent = TranslationAgent(
        translate_tool=FakeTranslateTool(),
        signal_extractor=TranslationSignalExtractor(),
        profile_updater=FakeTranslationProfileUpdater(),
        prompt_renderer=build_project_prompt_renderer(),
    )

    result = asyncio.run(
        agent.execute(
            TranslationRequest(
                learner_id="learner-1",
                source_text="我昨天去了图书馆。",
                direction="zh_to_en",
                user_translation="I go to library yesterday.",
            )
        )
    )

    assert result.standard_translation == "I went to the library yesterday."
    assert result.natural_translation == "I went to the library yesterday."
    assert [item.category for item in result.diagnosis_items] == [
        "grammar_error",
        "word_choice_issue",
    ]
    assert result.profile_update["preferred_direction"] == "zh_to_en"


def test_translation_agent_identifies_missing_content_and_unnatural_expression() -> None:
    agent = TranslationAgent(
        translate_tool=FakeTranslateTool(),
        signal_extractor=TranslationSignalExtractor(),
        profile_updater=FakeTranslationProfileUpdater(),
        prompt_renderer=build_project_prompt_renderer(),
    )

    result = asyncio.run(
        agent.execute(
            TranslationRequest(
                learner_id="learner-2",
                source_text="我昨天去了图书馆。",
                direction="zh_to_en",
                user_translation="Yesterday I did go.",
            )
        )
    )

    assert [item.category for item in result.diagnosis_items] == [
        "unnatural_expression",
        "missing_or_mistranslated_content",
    ]
    assert any("自然" in feedback or "完整" in feedback for feedback in result.learning_feedback)


def test_translation_agent_renders_feedback_from_external_prompt_templates(tmp_path) -> None:
    feedback_dir = tmp_path / "translation" / "feedback"
    feedback_dir.mkdir(parents=True)
    stage_dir = tmp_path / "translation" / "stages" / "senior_high_school"
    stage_dir.mkdir(parents=True)
    profile_dir = tmp_path / "translation" / "profile"
    profile_dir.mkdir(parents=True)
    (feedback_dir / "header.md").write_text("HEADER::{direction}", encoding="utf-8")
    (feedback_dir / "grammar_error.md").write_text("GRAMMAR::{issue}::{suggestion}", encoding="utf-8")
    (feedback_dir / "word_choice_issue.md").write_text("WORD::{issue}::{suggestion}", encoding="utf-8")
    (feedback_dir / "unnatural_expression.md").write_text("UNNATURAL::{issue}::{suggestion}", encoding="utf-8")
    (feedback_dir / "missing_or_mistranslated_content.md").write_text(
        "MISSING::{issue}::{suggestion}",
        encoding="utf-8",
    )
    (feedback_dir / "success.md").write_text("SUCCESS::{direction}", encoding="utf-8")
    (stage_dir / "strategy.md").write_text("STAGE::strategy::{stage}", encoding="utf-8")
    (stage_dir / "diagnosis.md").write_text("STAGE::diagnosis::{stage}", encoding="utf-8")
    (profile_dir / "grammar_focus.md").write_text("PROFILE::grammar::{weak_point}", encoding="utf-8")
    (profile_dir / "lexical_focus.md").write_text("PROFILE::lexical::{weak_point}", encoding="utf-8")
    (profile_dir / "literal_translation.md").write_text("PROFILE::literal", encoding="utf-8")

    agent = TranslationAgent(
        translate_tool=FakeTranslateTool(),
        signal_extractor=TranslationSignalExtractor(),
        profile_updater=FakeTranslationProfileUpdater(),
        prompt_renderer=PromptRenderer(PromptLoader(base_dir=tmp_path)),
    )

    result = asyncio.run(
        agent.execute(
            TranslationRequest(
                learner_id="learner-1",
                source_text="我昨天去了图书馆。",
                direction="zh_to_en",
                user_translation="I go to library yesterday.",
            )
        )
    )

    assert result.learning_feedback == [
        "HEADER::zh_to_en",
        "STAGE::strategy::senior_high_school",
        "STAGE::diagnosis::senior_high_school",
        "GRAMMAR::时态错误::went",
        "WORD::搭配或冠词使用不当::the library",
    ]


def test_translation_agent_uses_stage_and_existing_profile_to_adapt_feedback(tmp_path) -> None:
    feedback_dir = tmp_path / "translation" / "feedback"
    feedback_dir.mkdir(parents=True)
    stage_dir = tmp_path / "translation" / "stages" / "primary_school"
    stage_dir.mkdir(parents=True)
    profile_dir = tmp_path / "translation" / "profile"
    profile_dir.mkdir(parents=True)
    (feedback_dir / "header.md").write_text("HEADER::{direction}::{stage}", encoding="utf-8")
    (feedback_dir / "grammar_error.md").write_text("GRAMMAR::{issue}", encoding="utf-8")
    (feedback_dir / "word_choice_issue.md").write_text("WORD::{issue}", encoding="utf-8")
    (feedback_dir / "unnatural_expression.md").write_text("UNNATURAL::{issue}", encoding="utf-8")
    (feedback_dir / "missing_or_mistranslated_content.md").write_text("MISSING::{issue}", encoding="utf-8")
    (feedback_dir / "success.md").write_text("SUCCESS::{direction}", encoding="utf-8")
    (stage_dir / "strategy.md").write_text("STAGE::primary_school::strategy", encoding="utf-8")
    (stage_dir / "diagnosis.md").write_text("STAGE::primary_school::diagnosis", encoding="utf-8")
    (profile_dir / "grammar_focus.md").write_text("PROFILE::grammar::{weak_point}", encoding="utf-8")
    (profile_dir / "lexical_focus.md").write_text("PROFILE::lexical::{weak_point}", encoding="utf-8")
    (profile_dir / "literal_translation.md").write_text("PROFILE::literal", encoding="utf-8")

    current_profile = TranslationProfileSnapshot(
        learner_id="learner-1",
        current_stage="primary_school",
        grammar_weak_points={"时态错误": 3},
    )
    agent = TranslationAgent(
        translate_tool=FakeTranslateTool(),
        signal_extractor=TranslationSignalExtractor(),
        profile_updater=FakeTranslationProfileUpdater(current_profile=current_profile),
        prompt_renderer=PromptRenderer(PromptLoader(base_dir=tmp_path)),
    )

    result = asyncio.run(
        agent.execute(
            TranslationRequest(
                learner_id="learner-1",
                source_text="我昨天去了图书馆。",
                direction="zh_to_en",
                user_translation="I go to library yesterday.",
            )
        )
    )

    assert result.stage_used == "primary_school"
    assert "STAGE::primary_school::strategy" in result.learning_feedback
    assert "STAGE::primary_school::diagnosis" in result.learning_feedback
    assert "PROFILE::grammar::时态错误" in result.learning_feedback
