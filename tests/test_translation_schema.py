from app.schemas.translation import (
    DiagnosisItem,
    TranslationRequest,
    TranslationResponse,
    TranslationSignal,
)


def test_translation_request_accepts_diagnosis_mode_fields() -> None:
    request = TranslationRequest(
        learner_id="learner-1",
        source_text="我昨天去了图书馆。",
        direction="zh_to_en",
        user_translation="I go to library yesterday.",
        conversation_id="conv-1",
        stage="primary_school",
    )

    assert request.learner_id == "learner-1"
    assert request.direction == "zh_to_en"
    assert request.user_translation == "I go to library yesterday."
    assert request.stage == "primary_school"


def test_translation_response_contains_feedback_and_profile_update() -> None:
    response = TranslationResponse(
        learner_id="learner-1",
        direction="zh_to_en",
        stage_used="primary_school",
        standard_translation="I went to the library yesterday.",
        natural_translation="I went to the library yesterday.",
        diagnosis_items=[
            DiagnosisItem(
                category="grammar_error",
                issue="时态错误",
                suggestion="went",
                explanation="昨天发生的动作应用过去时。",
            )
        ],
        learning_feedback=[
            "yesterday 通常提示过去时。",
        ],
        profile_update={
            "preferred_direction": "zh_to_en",
            "literal_translation_tendency_count": 0,
        },
    )

    assert response.diagnosis_items[0].category == "grammar_error"
    assert response.stage_used == "primary_school"
    assert response.profile_update["preferred_direction"] == "zh_to_en"


def test_translation_signal_tracks_direction_and_error_types() -> None:
    signal = TranslationSignal(
        learner_id="learner-1",
        direction="zh_to_en",
        error_types=["grammar_error", "word_choice_issue"],
        grammar_weak_points=["tense"],
        lexical_weak_points=["word_choice"],
        literal_translation_tendency=False,
    )

    assert signal.direction == "zh_to_en"
    assert signal.error_types == ["grammar_error", "word_choice_issue"]
