from app.profile.models import TranslationProfileSnapshot
from app.schemas.translation import TranslationSignal, TranslationStage
from app.state.redis_store import RedisStateStore


class TranslationProfileUpdater:
    def __init__(self, state_store: RedisStateStore) -> None:
        self._state_store = state_store

    def load(self, learner_id: str) -> TranslationProfileSnapshot | None:
        return self._state_store.load_translation_profile(learner_id)

    def update(
        self,
        signal: TranslationSignal,
        stage: TranslationStage | None = None,
    ) -> TranslationProfileSnapshot:
        current = self.load(signal.learner_id)
        if current is None:
            current = TranslationProfileSnapshot(learner_id=signal.learner_id)

        if stage is not None:
            current.current_stage = stage
        current.preferred_direction = signal.direction
        current.direction_counts[signal.direction] = current.direction_counts.get(signal.direction, 0) + 1

        for error_type in signal.error_types:
            current.frequent_error_types[error_type] = current.frequent_error_types.get(error_type, 0) + 1

        for point in signal.grammar_weak_points:
            current.grammar_weak_points[point] = current.grammar_weak_points.get(point, 0) + 1

        for point in signal.lexical_weak_points:
            current.lexical_weak_points[point] = current.lexical_weak_points.get(point, 0) + 1

        if signal.literal_translation_tendency:
            current.literal_translation_tendency_count += 1

        self._state_store.save_translation_profile(current)
        return current
