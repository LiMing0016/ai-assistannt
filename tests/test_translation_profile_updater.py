from app.profile.models import TranslationProfileSnapshot
from app.profile.updater.translation_profile_updater import TranslationProfileUpdater
from app.schemas.translation import TranslationSignal
from app.state.redis_store import RedisStateStore


class FakeRedis:
    def __init__(self) -> None:
        self.values: dict[str, str] = {}

    def set(self, key: str, value: str) -> None:
        self.values[key] = value

    def get(self, key: str) -> str | None:
        return self.values.get(key)


def test_translation_profile_updater_creates_and_accumulates_profile() -> None:
    store = RedisStateStore(redis_url="redis://unused", client=FakeRedis())
    updater = TranslationProfileUpdater(state_store=store)

    first = updater.update(
        TranslationSignal(
            learner_id="learner-1",
            direction="zh_to_en",
            error_types=["grammar_error"],
            grammar_weak_points=["tense"],
            lexical_weak_points=[],
            literal_translation_tendency=False,
        ),
        stage="primary_school",
    )
    second = updater.update(
        TranslationSignal(
            learner_id="learner-1",
            direction="zh_to_en",
            error_types=["word_choice_issue"],
            grammar_weak_points=[],
            lexical_weak_points=["word_choice"],
            literal_translation_tendency=True,
        ),
        stage="ielts",
    )

    assert isinstance(first, TranslationProfileSnapshot)
    assert first.current_stage == "primary_school"
    assert second.current_stage == "ielts"
    assert second.preferred_direction == "zh_to_en"
    assert second.direction_counts["zh_to_en"] == 2
    assert second.frequent_error_types["grammar_error"] == 1
    assert second.frequent_error_types["word_choice_issue"] == 1
    assert second.grammar_weak_points["tense"] == 1
    assert second.lexical_weak_points["word_choice"] == 1
    assert second.literal_translation_tendency_count == 1
