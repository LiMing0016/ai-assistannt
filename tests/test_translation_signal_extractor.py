from app.profile.extractor.translation_signal_extractor import TranslationSignalExtractor
from app.schemas.translation import DiagnosisItem


def test_translation_signal_extractor_builds_structured_signal() -> None:
    extractor = TranslationSignalExtractor()

    signal = extractor.extract(
        learner_id="learner-1",
        direction="zh_to_en",
        diagnosis_items=[
            DiagnosisItem(
                category="grammar_error",
                issue="时态错误",
                suggestion="went",
                explanation="过去动作要用过去时。",
            ),
            DiagnosisItem(
                category="word_choice_issue",
                issue="library 前缺少冠词",
                suggestion="the library",
                explanation="这里通常说 the library。",
            ),
            DiagnosisItem(
                category="unnatural_expression",
                issue="表达比较直译",
                suggestion="I went to the library yesterday.",
                explanation="更自然的说法是完整句式。",
            ),
        ],
    )

    assert signal.direction == "zh_to_en"
    assert signal.error_types == ["grammar_error", "word_choice_issue", "unnatural_expression"]
    assert signal.grammar_weak_points == ["时态错误"]
    assert signal.lexical_weak_points == ["library 前缺少冠词"]
    assert signal.literal_translation_tendency is True


def test_translation_signal_extractor_marks_missing_content_as_grammar_weak_point_free() -> None:
    extractor = TranslationSignalExtractor()

    signal = extractor.extract(
        learner_id="learner-2",
        direction="zh_to_en",
        diagnosis_items=[
            DiagnosisItem(
                category="missing_or_mistranslated_content",
                issue="漏掉了地点信息",
                suggestion="the library",
                explanation="原句中的地点信息需要翻出来。",
            )
        ],
    )

    assert signal.error_types == ["missing_or_mistranslated_content"]
    assert signal.grammar_weak_points == []
    assert signal.lexical_weak_points == []
    assert signal.literal_translation_tendency is False
