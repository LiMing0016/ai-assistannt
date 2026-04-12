import asyncio

import pytest

from app.core.config import Settings
from app.providers.base import ProviderResponse
from app.services.assistant_service import AssistantService


class FakeProvider:
    async def generate(self, messages):
        assert messages == [{"role": "user", "content": "hello"}]
        return ProviderResponse(provider="kimi", model="moonshot-v1-8k", reply="你好")


class FakeStateStore:
    def __init__(self) -> None:
        self.enabled = True
        self.calls: list[tuple[str, list[object]]] = []

    def is_enabled(self) -> bool:
        return self.enabled

    def append_conversation_messages(self, conversation_id, messages) -> None:
        self.calls.append((conversation_id, messages))


@pytest.mark.anyio
async def test_assistant_service_uses_provider_and_persists_state(monkeypatch) -> None:
    calls: list[object] = []

    async def fake_to_thread(func, *args, **kwargs):
        calls.append(func)
        return func(*args, **kwargs)

    monkeypatch.setattr(asyncio, "to_thread", fake_to_thread)
    state_store = FakeStateStore()
    service = AssistantService(
        provider=FakeProvider(),
        state_store=state_store,
        settings=Settings(),
    )

    result = await service.chat("hello")

    assert result["reply"] == "你好"
    assert result["provider"] == "kimi"
    assert result["model"] == "moonshot-v1-8k"
    assert result["processor"] == "assistant"
    assert result["state"]["conversation_enabled"] is True
    assert result["state"]["task_state_enabled"] is True
    assert len(calls) == 1
    assert len(state_store.calls) == 1
    conversation_id, messages = state_store.calls[0]
    assert conversation_id == "default"
    assert [message.role for message in messages] == ["user", "assistant"]
    assert [message.content for message in messages] == ["hello", "你好"]
