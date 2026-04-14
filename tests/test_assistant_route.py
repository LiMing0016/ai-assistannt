from fastapi.testclient import TestClient

from app.core.dependencies import get_assistant_service
from app.main import create_app
from app.providers.errors import ProviderHTTPError, ProviderNotSupportedError, ProviderTimeoutError


class FakeAssistantService:
    async def chat(
        self,
        message: str,
        conversation_id: str | None = None,
        user_id: str | None = None,
        stage: str | None = None,
        provider: str | None = None,
        model: str | None = None,
    ) -> dict[str, object]:
        assert message == "hello"
        assert conversation_id == "conv-1"
        assert user_id == "user-1"
        assert stage == "ielts"
        assert provider == "openai"
        assert model == "gpt-5-mini"
        return {
            "reply": "你好，我是 OpenAI。",
            "provider": "openai",
            "model": "gpt-5-mini",
            "processor": "assistant",
            "tracing": {"langsmith_enabled": False, "project": None},
            "state": {
                "conversation_enabled": True,
                "task_state_enabled": True,
            },
            "debug": {
                "loaded_skills": ["translation-learning"],
                "resolved_stage": "ielts",
                "stage_source": "manual",
                "loaded_stage_context": True,
                "history_messages_loaded": 4,
                "history_messages_trimmed": 0,
                "context_window_tokens": 400000,
                "estimated_input_tokens": 96,
                "input_budget_tokens": 383616,
                "system_prompt": "prompt",
                "request_messages": [
                    {"role": "system", "content": "prompt"},
                    {"role": "user", "content": "hello"},
                ],
            },
            "usage": {
                "prompt_tokens": 120,
                "completion_tokens": 18,
                "total_tokens": 138,
                "cached_tokens": 80,
                "cache_hit_ratio": 80 / 120,
            },
        }


def test_assistant_chat_returns_provider_model_and_reply() -> None:
    app = create_app()
    app.dependency_overrides[get_assistant_service] = lambda: FakeAssistantService()
    client = TestClient(app)

    response = client.post(
        "/assistant/chat",
        json={
            "message": "hello",
            "conversation_id": "conv-1",
            "user_id": "user-1",
            "stage": "ielts",
            "provider": "openai",
            "model": "gpt-5-mini",
        },
    )

    assert response.status_code == 200
    assert response.json()["reply"] == "你好，我是 OpenAI。"
    assert response.json()["provider"] == "openai"
    assert response.json()["model"] == "gpt-5-mini"
    assert response.json()["processor"] == "assistant"
    assert response.json()["tracing"]["langsmith_enabled"] is False
    assert response.json()["state"]["conversation_enabled"] is True
    assert response.json()["debug"]["resolved_stage"] == "ielts"
    assert response.json()["debug"]["loaded_skills"] == ["translation-learning"]
    assert response.json()["debug"]["history_messages_loaded"] == 4
    assert response.json()["debug"]["request_messages"][0]["role"] == "system"
    assert response.json()["usage"]["cached_tokens"] == 80
    assert response.json()["trace_id"]


def test_chat_page_returns_html() -> None:
    app = create_app()
    client = TestClient(app)

    response = client.get("/chat")

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "AI Assistant Chat" in response.text
    assert "System Prompt" in response.text
    assert "Full Prompt Messages" in response.text
    assert "promptMessages" in response.text
    assert "renderPromptMessages" in response.text
    assert "Usage" in response.text
    assert "Prompt Tokens" in response.text
    assert "dashscope" in response.text
    assert "moonshot-v1-8k" in response.text
    assert "qwen-plus" in response.text


def test_assistant_chat_returns_504_for_provider_timeout() -> None:
    class TimeoutAssistantService:
        async def chat(self, *args, **kwargs):
            raise ProviderTimeoutError("provider request timed out")

    app = create_app()
    app.dependency_overrides[get_assistant_service] = lambda: TimeoutAssistantService()
    client = TestClient(app)

    response = client.post("/assistant/chat", json={"message": "hello"})

    assert response.status_code == 504
    assert response.json()["detail"] == "provider request timed out"


def test_assistant_chat_returns_400_for_unsupported_provider() -> None:
    class UnsupportedAssistantService:
        async def chat(self, *args, **kwargs):
            raise ProviderNotSupportedError("Unsupported provider: claude")

    app = create_app()
    app.dependency_overrides[get_assistant_service] = lambda: UnsupportedAssistantService()
    client = TestClient(app)

    response = client.post("/assistant/chat", json={"message": "hello"})

    assert response.status_code == 400
    assert response.json()["detail"] == "Unsupported provider: claude"


def test_assistant_chat_returns_upstream_status_for_provider_http_error() -> None:
    class UpstreamErrorAssistantService:
        async def chat(self, *args, **kwargs):
            raise ProviderHTTPError(status_code=401, message="Invalid API key")

    app = create_app()
    app.dependency_overrides[get_assistant_service] = lambda: UpstreamErrorAssistantService()
    client = TestClient(app)

    response = client.post("/assistant/chat", json={"message": "hello"})

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid API key"
