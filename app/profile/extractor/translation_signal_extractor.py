from app.schemas.translation import DiagnosisItem, TranslationSignal


class TranslationSignalExtractor:
    def extract(
        self,
        learner_id: str,
        direction: str,
        diagnosis_items: list[DiagnosisItem],
    ) -> TranslationSignal:
        error_types: list[str] = []
        grammar_weak_points: list[str] = []
        lexical_weak_points: list[str] = []
        literal_translation_tendency = False

        for item in diagnosis_items:
            if item.category not in error_types:
                error_types.append(item.category)
            if item.category == "grammar_error":
                grammar_weak_points.append(item.issue)
            if item.category == "word_choice_issue":
                lexical_weak_points.append(item.issue)
            if item.category == "unnatural_expression":
                literal_translation_tendency = True

        return TranslationSignal(
            learner_id=learner_id,
            direction=direction,
            error_types=error_types,
            grammar_weak_points=grammar_weak_points,
            lexical_weak_points=lexical_weak_points,
            literal_translation_tendency=literal_translation_tendency,
        )
