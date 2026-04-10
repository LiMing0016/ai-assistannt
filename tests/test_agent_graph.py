import asyncio

import pytest

from app.core.config import Settings
from app.graphs.agent_graph import AgentGraphService
from app.integrations.backend_client import ExplainKnowledgeResponse


class FakeBackendClient:
    async def explain_english_knowledge(self, message: str) -> ExplainKnowledgeResponse:
        return ExplainKnowledgeResponse(reply=f"Explained: {message}")


class FakeStateStore:
    def __init__(self) -> None:
        self.enabled = True
        self.append_calls = 0

    def is_enabled(self) -> bool:
        return self.enabled

    def append_conversation_messages(self, conversation_id, messages) -> None:
        self.append_calls += 1


@pytest.mark.anyio
async def test_agent_graph_uses_to_thread_for_state_write(monkeypatch) -> None:
    calls: list[object] = []

    async def fake_to_thread(func, *args, **kwargs):
        calls.append(func)
        return func(*args, **kwargs)

    monkeypatch.setattr(asyncio, "to_thread", fake_to_thread)
    state_store = FakeStateStore()
    service = AgentGraphService(
        backend_client=FakeBackendClient(),
        state_store=state_store,
        settings=Settings(),
    )

    result = await service.execute("hello")

    assert result["reply"] == "Explained: hello"
    assert state_store.append_calls == 1
    assert len(calls) == 1
