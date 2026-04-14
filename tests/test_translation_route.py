from fastapi.testclient import TestClient

from app.core.dependencies import get_translation_service
from app.integrations.errors import BackendHTTPError, BackendTimeoutError
from app.main import create_app


class FakeTranslationService:
    async def execute(self, payload):
        assert payload.learner_id == "learner-1"
        assert payload.direction == "zh_to_en"
        return {
            "learner_id": "learner-1",
            "direction": "zh_to_en",
            "stage_used": "senior_high_school",
            "standard_translation": "I went to the library yesterday.",
            "natural_translation": "I went to the library yesterday.",
            "diagnosis_items": [
                {
                    "category": "missing_or_mistranslated_content",
                    "issue": "译文未准确表达原句含义。",
                    "suggestion": "I went to the library yesterday.",
                    "explanation": "原句是过去发生的动作。",
                }
            ],
            "learning_feedback": ["yesterday 通常提示过去时。"],
            "profile_update": {
                "preferred_direction": "zh_to_en",
                "direction_counts": {"zh_to_en": 1},
            },
        }


def test_translation_execute_returns_translation_and_profile_update() -> None:
    app = create_app()
    app.dependency_overrides[get_translation_service] = lambda: FakeTranslationService()
    client = TestClient(app)

    response = client.post(
        "/translation/execute",
        json={
            "learner_id": "learner-1",
            "source_text": "我昨天去了图书馆。",
            "direction": "zh_to_en",
            "user_translation": "I go to library yesterday.",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["standard_translation"] == "I went to the library yesterday."
    assert body["diagnosis_items"][0]["category"] == "missing_or_mistranslated_content"
    assert body["profile_update"]["preferred_direction"] == "zh_to_en"


def test_translation_execute_returns_504_for_backend_timeout() -> None:
    class TimeoutTranslationService:
        async def execute(self, payload):
            raise BackendTimeoutError("backend translate request timed out")

    app = create_app()
    app.dependency_overrides[get_translation_service] = lambda: TimeoutTranslationService()
    client = TestClient(app)

    response = client.post(
        "/translation/execute",
        json={
            "learner_id": "learner-1",
            "source_text": "我昨天去了图书馆。",
            "direction": "zh_to_en",
        },
    )

    assert response.status_code == 504
    assert response.json()["detail"] == "backend translate request timed out"


def test_translation_execute_returns_upstream_status_for_backend_http_error() -> None:
    class UnauthorizedTranslationService:
        async def execute(self, payload):
            raise BackendHTTPError(status_code=401, message="Unauthorized")

    app = create_app()
    app.dependency_overrides[get_translation_service] = lambda: UnauthorizedTranslationService()
    client = TestClient(app)

    response = client.post(
        "/translation/execute",
        json={
            "learner_id": "learner-1",
            "source_text": "我昨天去了图书馆。",
            "direction": "zh_to_en",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Unauthorized"
