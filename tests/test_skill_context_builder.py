import shutil
import uuid
from pathlib import Path

from app.skills.context_builder import SkillContextBuilder


def _make_test_skills_dir() -> Path:
    base_dir = Path("tmp") / f"skill-context-{uuid.uuid4().hex}"
    skills_dir = base_dir / "skills"
    (skills_dir / "translation-learning" / "references").mkdir(parents=True)
    (skills_dir / "translation-learning" / "SKILL.md").write_text("# Translation Learning", encoding="utf-8")
    (skills_dir / "translation-learning" / "references" / "runtime.md").write_text(
        "# Runtime\n## Skill Routing\nruntime-rules",
        encoding="utf-8",
    )
    (skills_dir / "translation-learning" / "references" / "workflow.md").write_text(
        "# Workflow", encoding="utf-8"
    )
    (skills_dir / "translation-learning" / "references" / "diagnosis-labels.md").write_text(
        "# Labels", encoding="utf-8"
    )
    (skills_dir / "translation-learning" / "references" / "output-patterns.md").write_text(
        "# Patterns", encoding="utf-8"
    )
    return skills_dir


def test_skill_context_builder_returns_base_prompt_for_non_translation_request() -> None:
    skills_dir = _make_test_skills_dir()
    try:
        builder = SkillContextBuilder(skills_base_dir=skills_dir, base_system_prompt="BASE PROMPT")

        result = builder.build("Explain present perfect simply")

        assert result["system_prompt"] == "BASE PROMPT"
        assert result["loaded_skills"] == []
        assert result["resolved_stage"] is None
        assert result["stage_source"] == "none"
        assert result["loaded_stage_context"] is False
    finally:
        shutil.rmtree(skills_dir.parent, ignore_errors=True)


def test_skill_context_builder_loads_translation_skill_for_translation_request() -> None:
    skills_dir = _make_test_skills_dir()
    (skills_dir / "translation-learning" / "SKILL.md").write_text(
        "# Translation Learning\nskill-overview",
        encoding="utf-8",
    )
    (skills_dir / "translation-learning" / "references" / "workflow.md").write_text(
        "# Workflow\nworkflow-rules",
        encoding="utf-8",
    )
    (skills_dir / "translation-learning" / "references" / "diagnosis-labels.md").write_text(
        "# Labels\ndiagnosis-rules",
        encoding="utf-8",
    )
    (skills_dir / "translation-learning" / "references" / "output-patterns.md").write_text(
        "# Patterns\noutput-rules",
        encoding="utf-8",
    )
    try:
        builder = SkillContextBuilder(skills_base_dir=skills_dir, base_system_prompt="BASE PROMPT")

        result = builder.build("请帮我翻译这句话：我昨天去了图书馆。")

        prompt = result["system_prompt"]
        assert "BASE PROMPT" in prompt
        assert "## Loaded Skill: translation-learning" in prompt
        assert "## Skill Routing" in prompt
        assert "runtime-rules" in prompt
        assert "skill-overview" not in prompt
        assert "workflow-rules" not in prompt
        assert result["loaded_skills"] == ["translation-learning"]
    finally:
        shutil.rmtree(skills_dir.parent, ignore_errors=True)


def test_skill_context_builder_loads_translation_skill_for_diagnosis_style_request() -> None:
    skills_dir = _make_test_skills_dir()
    try:
        builder = SkillContextBuilder(skills_base_dir=skills_dir, base_system_prompt="BASE PROMPT")

        result = builder.build("我写的是 I go to library yesterday. 这样翻对吗？请帮我改一下并解释。")

        assert "## Loaded Skill: translation-learning" in result["system_prompt"]
    finally:
        shutil.rmtree(skills_dir.parent, ignore_errors=True)


def test_skill_context_builder_loads_matching_stage_reference_when_stage_is_present() -> None:
    skills_dir = _make_test_skills_dir()
    stages_dir = skills_dir / "translation-learning" / "references" / "stages"
    stages_dir.mkdir(parents=True, exist_ok=True)
    (stages_dir / "ielts.md").write_text("# IELTS\nielts-stage-rules", encoding="utf-8")

    try:
        builder = SkillContextBuilder(
            skills_base_dir=skills_dir,
            base_system_prompt="BASE PROMPT",
            stage_resolver=lambda user_id: "ielts" if user_id == "user-1" else None,
        )

        result = builder.build("请帮我把这句中文翻成英文，并指出我译文的问题。", user_id="user-1")

        assert "ielts-stage-rules" in result["system_prompt"]
        assert result["resolved_stage"] == "ielts"
        assert result["stage_source"] == "profile"
        assert result["loaded_stage_context"] is True
    finally:
        shutil.rmtree(skills_dir.parent, ignore_errors=True)


def test_skill_context_builder_maps_underscore_stage_name_to_stage_file() -> None:
    skills_dir = _make_test_skills_dir()
    stages_dir = skills_dir / "translation-learning" / "references" / "stages"
    stages_dir.mkdir(parents=True, exist_ok=True)
    (stages_dir / "primary-school.md").write_text(
        "# Primary School\nprimary-stage-rules",
        encoding="utf-8",
    )

    try:
        builder = SkillContextBuilder(
            skills_base_dir=skills_dir,
            base_system_prompt="BASE PROMPT",
            stage_resolver=lambda user_id: "primary_school" if user_id == "user-1" else None,
        )

        result = builder.build("请帮我把这句中文翻成英文。", user_id="user-1")

        assert "primary-stage-rules" in result["system_prompt"]
        assert result["resolved_stage"] == "primary_school"
    finally:
        shutil.rmtree(skills_dir.parent, ignore_errors=True)


def test_skill_context_builder_does_not_load_stage_reference_when_stage_is_missing() -> None:
    skills_dir = _make_test_skills_dir()
    stages_dir = skills_dir / "translation-learning" / "references" / "stages"
    stages_dir.mkdir(parents=True, exist_ok=True)
    (stages_dir / "ielts.md").write_text("# IELTS\nielts-stage-rules", encoding="utf-8")

    try:
        builder = SkillContextBuilder(
            skills_base_dir=skills_dir,
            base_system_prompt="BASE PROMPT",
            stage_resolver=lambda _user_id: None,
        )

        result = builder.build("请帮我把这句中文翻成英文。", user_id="user-1")

        assert "ielts-stage-rules" not in result["system_prompt"]
        assert result["resolved_stage"] is None
        assert result["loaded_stage_context"] is False
    finally:
        shutil.rmtree(skills_dir.parent, ignore_errors=True)
