from fastapi.testclient import TestClient

from app.core.dependencies import get_backend_client, get_state_store
from app.integrations.backend_client import ExplainKnowledgeResponse
from app.main import create_app


class FakeBackendClient:
    async def explain_english_knowledge(self, message: str) -> ExplainKnowledgeResponse:
        return ExplainKnowledgeResponse(reply=f"Explained: {message}")


class FakeStateStore:
    def is_enabled(self) -> bool:
        return True

    def append_conversation_messages(self, conversation_id, messages) -> None:
        return None


def test_agent_execute_returns_placeholder_reply() -> None:
    app = create_app()
    app.dependency_overrides[get_backend_client] = lambda: FakeBackendClient()
    app.dependency_overrides[get_state_store] = lambda: FakeStateStore()
    client = TestClient(app)

    response = client.post("/agent/execute", json={"message": "hello"})

    assert response.status_code == 200
    assert response.json()["reply"] == "Explained: hello"
    assert response.json()["processor"] == "langgraph"
    assert response.json()["tool"] == "explain_english_knowledge"
    assert response.json()["tracing"]["langsmith_enabled"] is False
    assert response.json()["state"]["conversation_enabled"] is True
    assert response.json()["state"]["task_state_enabled"] is True
    assert response.json()["trace_id"]
