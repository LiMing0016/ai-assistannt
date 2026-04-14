from functools import lru_cache
from pathlib import Path
from typing import Callable


class SkillPromptContext(dict):
    pass


class SkillContextBuilder:
    def __init__(
        self,
        skills_base_dir: str | Path,
        base_system_prompt: str,
        stage_resolver: Callable[[str], str | None] | None = None,
    ) -> None:
        self._skills_base_dir = Path(skills_base_dir)
        self._base_system_prompt = base_system_prompt.strip()
        self._stage_resolver = stage_resolver

    def build(
        self,
        message: str,
        user_id: str | None = None,
        stage_override: str | None = None,
    ) -> SkillPromptContext:
        if not self._should_load_translation_skill(message):
            return SkillPromptContext(
                system_prompt=self._base_system_prompt,
                loaded_skills=[],
                resolved_stage=None,
                stage_source="none",
                loaded_stage_context=False,
            )

        sections = [
            self._base_system_prompt,
            "## Loaded Skill: translation-learning",
            self._load_runtime_skill_text(),
        ]
        resolved_stage = stage_override or self._resolve_stage(user_id)
        stage_source = "manual" if stage_override else "profile" if resolved_stage else "none"
        loaded_stage_context = False
        if resolved_stage:
            stage_file_name = resolved_stage.replace("_", "-")
            stage_text = self._load_optional_text(
                f"translation-learning/references/stages/{stage_file_name}.md"
            )
            if stage_text:
                sections.append(f"## Stage Context: {resolved_stage}")
                sections.append(stage_text)
                loaded_stage_context = True
        return SkillPromptContext(
            system_prompt="\n\n".join(section for section in sections if section),
            loaded_skills=["translation-learning"],
            resolved_stage=resolved_stage,
            stage_source=stage_source,
            loaded_stage_context=loaded_stage_context,
        )

    @staticmethod
    def _should_load_translation_skill(message: str) -> bool:
        normalized = message.lower()
        chinese_keywords = [
            "翻译",
            "翻成",
            "译成",
            "译文",
            "中译英",
            "英译中",
            "怎么说",
            "啥意思",
            "翻对吗",
            "这样翻对不对",
            "这样翻对吗",
            "我这样翻对不对",
            "我写的是",
            "帮我改一下",
            "我这么写行不行",
        ]
        english_keywords = [
            "translate",
            "translation",
            "translate this",
            "how do you say",
            "is this translation correct",
        ]
        return any(keyword in message for keyword in chinese_keywords) or any(
            keyword in normalized for keyword in english_keywords
        )

    def _load_text(self, relative_path: str) -> str:
        return self._load_text_cached(str(self._skills_base_dir), relative_path)

    def _load_optional_text(self, relative_path: str) -> str | None:
        path = self._skills_base_dir / relative_path
        if not path.exists():
            return None
        return self._load_text(relative_path)

    def _load_runtime_skill_text(self) -> str:
        runtime_text = self._load_optional_text("translation-learning/references/runtime.md")
        if runtime_text:
            return runtime_text
        return "\n\n".join(
            [
                self._load_text("translation-learning/SKILL.md"),
                self._load_text("translation-learning/references/workflow.md"),
                self._load_text("translation-learning/references/diagnosis-labels.md"),
                self._load_text("translation-learning/references/output-patterns.md"),
            ]
        )

    def _resolve_stage(self, user_id: str | None) -> str | None:
        if not user_id or self._stage_resolver is None:
            return None
        return self._stage_resolver(user_id)

    @staticmethod
    @lru_cache(maxsize=64)
    def _load_text_cached(skills_base_dir: str, relative_path: str) -> str:
        return (Path(skills_base_dir) / relative_path).read_text(encoding="utf-8").strip()
