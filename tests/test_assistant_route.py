from fastapi.testclient import TestClient

from app.core.dependencies import get_assistant_service
from app.main import create_app


class FakeAssistantService:
    async def chat(self, message: str, conversation_id: str | None = None) -> dict[str, object]:
        assert message == "hello"
        assert conversation_id == "conv-1"
        return {
            "reply": "你好，我是 Kimi。",
            "provider": "kimi",
            "model": "moonshot-v1-8k",
            "processor": "assistant",
            "tracing": {"langsmith_enabled": False, "project": None},
            "state": {
                "conversation_enabled": True,
                "task_state_enabled": True,
            },
        }


def test_assistant_chat_returns_provider_model_and_reply() -> None:
    app = create_app()
    app.dependency_overrides[get_assistant_service] = lambda: FakeAssistantService()
    client = TestClient(app)

    response = client.post(
        "/assistant/chat",
        json={"message": "hello", "conversation_id": "conv-1"},
    )

    assert response.status_code == 200
    assert response.json()["reply"] == "你好，我是 Kimi。"
    assert response.json()["provider"] == "kimi"
    assert response.json()["model"] == "moonshot-v1-8k"
    assert response.json()["processor"] == "assistant"
    assert response.json()["tracing"]["langsmith_enabled"] is False
    assert response.json()["state"]["conversation_enabled"] is True
    assert response.json()["trace_id"]
