from typing import Literal

from pydantic import BaseModel, Field


TranslationDirection = Literal["zh_to_en", "en_to_zh"]
TranslationStage = Literal[
    "primary_school",
    "junior_high_school",
    "senior_high_school",
    "cet",
    "postgraduate_exam",
    "ielts",
    "toefl",
]
DiagnosisCategory = Literal[
    "grammar_error",
    "word_choice_issue",
    "unnatural_expression",
    "missing_or_mistranslated_content",
]


class TranslationRequest(BaseModel):
    learner_id: str = Field(min_length=1)
    source_text: str = Field(min_length=1)
    direction: TranslationDirection
    stage: TranslationStage | None = None
    user_translation: str | None = None
    conversation_id: str | None = None


class DiagnosisItem(BaseModel):
    category: DiagnosisCategory
    issue: str
    suggestion: str
    explanation: str


class TranslationSignal(BaseModel):
    learner_id: str
    direction: TranslationDirection
    error_types: list[DiagnosisCategory] = Field(default_factory=list)
    grammar_weak_points: list[str] = Field(default_factory=list)
    lexical_weak_points: list[str] = Field(default_factory=list)
    literal_translation_tendency: bool = False


class TranslationResponse(BaseModel):
    learner_id: str
    direction: TranslationDirection
    stage_used: TranslationStage
    standard_translation: str
    natural_translation: str
    diagnosis_items: list[DiagnosisItem] = Field(default_factory=list)
    learning_feedback: list[str] = Field(default_factory=list)
    profile_update: dict[str, object] = Field(default_factory=dict)
