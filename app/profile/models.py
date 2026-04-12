from pydantic import BaseModel, Field


class LearnerCapabilityProfile(BaseModel):
    learner_id: str
    target_subject: str = "english"
    vocabulary_level: str | None = None
    grammar_level: str | None = None
    writing_level: str | None = None
    learning_goal: str | None = None
    preferred_explanation_style: str | None = None
    weak_points: list[str] = Field(default_factory=list)

