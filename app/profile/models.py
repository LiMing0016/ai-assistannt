from pydantic import BaseModel, Field

from app.schemas.translation import TranslationStage


class LearnerCapabilityProfile(BaseModel):
    learner_id: str
    target_subject: str = "english"
    vocabulary_level: str | None = None
    grammar_level: str | None = None
    writing_level: str | None = None
    learning_goal: str | None = None
    preferred_explanation_style: str | None = None
    weak_points: list[str] = Field(default_factory=list)


class TranslationProfileSnapshot(BaseModel):
    learner_id: str
    current_stage: TranslationStage | None = None
    preferred_direction: str | None = None
    direction_counts: dict[str, int] = Field(default_factory=dict)
    frequent_error_types: dict[str, int] = Field(default_factory=dict)
    grammar_weak_points: dict[str, int] = Field(default_factory=dict)
    lexical_weak_points: dict[str, int] = Field(default_factory=dict)
    literal_translation_tendency_count: int = 0

