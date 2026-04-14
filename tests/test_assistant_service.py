import asyncio

import pytest

from app.core.config import Settings
from app.providers.base import ProviderResponse, ProviderUsage
from app.state.models import ConversationMessage, ConversationState
from app.services.assistant_service import AssistantService


class FakeProvider:
    def __init__(self, provider_name: str = "kimi", model_name: str = "moonshot-v1-8k") -> None:
        self.provider_name = provider_name
        self.model_name = model_name

    async def generate(self, messages):
        assert messages == [
            {"role": "system", "content": "You are the English learning assistant."},
            {"role": "user", "content": "hello"},
        ]
        return ProviderResponse(
            provider=self.provider_name,
            model=self.model_name,
            reply="你好",
            usage=ProviderUsage(prompt_tokens=12, completion_tokens=4, total_tokens=16, cached_tokens=0),
        )


class CapturingProvider:
    def __init__(self, provider_name: str = "kimi", model_name: str = "moonshot-v1-8k") -> None:
        self.provider_name = provider_name
        self.model_name = model_name
        self.messages = None

    async def generate(self, messages):
        self.messages = messages
        return ProviderResponse(
            provider=self.provider_name,
            model=self.model_name,
            reply="ok",
            usage=ProviderUsage(prompt_tokens=24, completion_tokens=6, total_tokens=30, cached_tokens=8),
        )


class FakeStateStore:
    def __init__(self) -> None:
        self.enabled = True
        self.calls: list[tuple[str, list[object]]] = []
        self.preferences: dict[str, tuple[str, str]] = {}
        self.conversations: dict[str, list[ConversationMessage]] = {}

    def is_enabled(self) -> bool:
        return self.enabled

    def append_conversation_messages(self, conversation_id, messages) -> None:
        self.calls.append((conversation_id, messages))
        self.conversations.setdefault(conversation_id, [])
        self.conversations[conversation_id].extend(messages)

    def load_conversation_state(self, conversation_id):
        return ConversationState(
            conversation_id=conversation_id,
            messages=list(self.conversations.get(conversation_id, [])),
        )

    def load_conversation_preference(self, conversation_id):
        current = self.preferences.get(conversation_id)
        if current is None:
            return None
        provider, model = current
        return type(
            "ConversationPreference",
            (),
            {
                "conversation_id": conversation_id,
                "provider": provider,
                "model": model,
            },
        )()

    def save_conversation_preference(self, preference) -> None:
        self.preferences[preference.conversation_id] = (preference.provider, preference.model)


@pytest.mark.anyio
async def test_assistant_service_uses_provider_and_persists_state(monkeypatch) -> None:
    calls: list[object] = []

    async def fake_to_thread(func, *args, **kwargs):
        calls.append(func)
        return func(*args, **kwargs)

    monkeypatch.setattr(asyncio, "to_thread", fake_to_thread)
    state_store = FakeStateStore()
    service = AssistantService(
        provider_factory=lambda *_args, **_kwargs: FakeProvider(),
        state_store=state_store,
        settings=Settings(),
        system_prompt_builder=lambda _message, _user_id=None, _stage_override=None: "You are the English learning assistant.",
    )

    result = await service.chat("hello")

    assert result["reply"] == "你好"
    assert result["provider"] == "kimi"
    assert result["model"] == "moonshot-v1-8k"
    assert result["processor"] == "assistant"
    assert result["state"]["conversation_enabled"] is True
    assert result["state"]["task_state_enabled"] is True
    assert result["debug"]["loaded_skills"] == []
    assert result["debug"]["resolved_stage"] is None
    assert result["debug"]["stage_source"] == "none"
    assert result["debug"]["history_messages_loaded"] == 0
    assert result["debug"]["history_messages_trimmed"] == 0
    assert result["debug"]["context_window_tokens"] == 8192
    assert result["debug"]["input_budget_tokens"] == 7168
    assert result["debug"]["estimated_input_tokens"] > 0
    assert result["debug"]["system_prompt"] == "You are the English learning assistant."
    assert result["debug"]["request_messages"] == [
        {"role": "system", "content": "You are the English learning assistant."},
        {"role": "user", "content": "hello"},
    ]
    assert result["usage"] == {
        "prompt_tokens": 12,
        "completion_tokens": 4,
        "total_tokens": 16,
        "cached_tokens": 0,
        "cache_hit_ratio": 0.0,
    }
    assert len(calls) == 3
    assert len(state_store.calls) == 1
    conversation_id, messages = state_store.calls[0]
    assert conversation_id == "default"
    assert [message.role for message in messages] == ["user", "assistant"]
    assert [message.content for message in messages] == ["hello", "你好"]


@pytest.mark.anyio
async def test_assistant_service_uses_request_provider_and_model_override(monkeypatch) -> None:
    calls: list[tuple[str | None, str | None]] = []

    async def fake_to_thread(func, *args, **kwargs):
        return func(*args, **kwargs)

    def provider_factory(provider_name: str | None, model_name: str | None):
        calls.append((provider_name, model_name))
        return FakeProvider(provider_name="openai", model_name="gpt-5-mini")

    monkeypatch.setattr(asyncio, "to_thread", fake_to_thread)
    service = AssistantService(
        provider_factory=provider_factory,
        state_store=FakeStateStore(),
        settings=Settings(),
        system_prompt_builder=lambda _message, _user_id=None, _stage_override=None: "You are the English learning assistant.",
    )

    result = await service.chat(
        "hello",
        conversation_id="conv-2",
        provider="openai",
        model="gpt-5-mini",
    )

    assert calls == [("openai", "gpt-5-mini")]
    assert result["provider"] == "openai"
    assert result["model"] == "gpt-5-mini"


@pytest.mark.anyio
async def test_assistant_service_reuses_saved_conversation_preference(monkeypatch) -> None:
    calls: list[tuple[str | None, str | None]] = []

    async def fake_to_thread(func, *args, **kwargs):
        return func(*args, **kwargs)

    def provider_factory(provider_name: str | None, model_name: str | None):
        calls.append((provider_name, model_name))
        return FakeProvider(provider_name=provider_name or "kimi", model_name=model_name or "moonshot-v1-8k")

    monkeypatch.setattr(asyncio, "to_thread", fake_to_thread)
    state_store = FakeStateStore()
    state_store.preferences["conv-memory"] = ("dashscope", "qwen-plus")
    service = AssistantService(
        provider_factory=provider_factory,
        state_store=state_store,
        settings=Settings(),
        system_prompt_builder=lambda _message, _user_id=None, _stage_override=None: "You are the English learning assistant.",
    )

    result = await service.chat("hello", conversation_id="conv-memory")

    assert calls == [("dashscope", "qwen-plus")]
    assert result["provider"] == "dashscope"
    assert result["model"] == "qwen-plus"


@pytest.mark.anyio
async def test_assistant_service_persists_conversation_preference_override(monkeypatch) -> None:
    async def fake_to_thread(func, *args, **kwargs):
        return func(*args, **kwargs)

    monkeypatch.setattr(asyncio, "to_thread", fake_to_thread)
    state_store = FakeStateStore()
    service = AssistantService(
        provider_factory=lambda provider_name, model_name: FakeProvider(
            provider_name=provider_name or "openai",
            model_name=model_name or "gpt-5-mini",
        ),
        state_store=state_store,
        settings=Settings(),
        system_prompt_builder=lambda _message, _user_id=None, _stage_override=None: "You are the English learning assistant.",
    )

    await service.chat(
        "hello",
        conversation_id="conv-save",
        provider="openai",
        model="gpt-5-mini",
    )

    assert state_store.preferences["conv-save"] == ("openai", "gpt-5-mini")


@pytest.mark.anyio
async def test_assistant_service_passes_user_id_into_system_prompt_builder(monkeypatch) -> None:
    async def fake_to_thread(func, *args, **kwargs):
        return func(*args, **kwargs)

    monkeypatch.setattr(asyncio, "to_thread", fake_to_thread)
    provider = CapturingProvider()
    received: list[tuple[str, str | None, str | None]] = []
    service = AssistantService(
        provider_factory=lambda *_args, **_kwargs: provider,
        state_store=FakeStateStore(),
        settings=Settings(),
        system_prompt_builder=lambda message, user_id=None, stage_override=None: (
            received.append((message, user_id, stage_override)) or f"prompt-for-{user_id}"
        ),
    )

    await service.chat("请帮我翻译这句话", conversation_id="conv-user", user_id="user-1")

    assert received == [("请帮我翻译这句话", "user-1", None)]
    assert provider.messages[0] == {"role": "system", "content": "prompt-for-user-1"}


@pytest.mark.anyio
async def test_assistant_service_returns_debug_metadata_from_system_prompt_builder(monkeypatch) -> None:
    async def fake_to_thread(func, *args, **kwargs):
        return func(*args, **kwargs)

    monkeypatch.setattr(asyncio, "to_thread", fake_to_thread)
    provider = CapturingProvider()
    service = AssistantService(
        provider_factory=lambda *_args, **_kwargs: provider,
        state_store=FakeStateStore(),
        settings=Settings(),
        system_prompt_builder=lambda message, user_id=None, stage_override=None: {
            "system_prompt": f"prompt-for-{message}-{user_id}-{stage_override}",
            "loaded_skills": ["translation-learning"],
            "resolved_stage": "ielts",
            "stage_source": "manual",
            "loaded_stage_context": True,
        },
    )

    result = await service.chat(
        "请帮我翻译这句话",
        conversation_id="conv-user",
        user_id="user-1",
        stage="ielts",
    )

    assert provider.messages[0]["content"] == "prompt-for-请帮我翻译这句话-user-1-ielts"
    assert result["debug"]["loaded_skills"] == ["translation-learning"]
    assert result["debug"]["resolved_stage"] == "ielts"
    assert result["debug"]["stage_source"] == "manual"
    assert result["debug"]["loaded_stage_context"] is True
    assert result["debug"]["history_messages_loaded"] == 0
    assert result["debug"]["history_messages_trimmed"] == 0
    assert result["debug"]["context_window_tokens"] == 8192
    assert result["debug"]["input_budget_tokens"] == 7168
    assert result["debug"]["estimated_input_tokens"] > 0
    assert result["debug"]["system_prompt"] == "prompt-for-请帮我翻译这句话-user-1-ielts"
    assert result["debug"]["request_messages"][0]["role"] == "system"
    assert result["debug"]["request_messages"][-1] == {"role": "user", "content": "请帮我翻译这句话"}
    assert result["usage"] == {
        "prompt_tokens": 24,
        "completion_tokens": 6,
        "total_tokens": 30,
        "cached_tokens": 8,
        "cache_hit_ratio": 8 / 24,
    }


@pytest.mark.anyio
async def test_assistant_service_loads_conversation_history_into_provider_messages(monkeypatch) -> None:
    async def fake_to_thread(func, *args, **kwargs):
        return func(*args, **kwargs)

    monkeypatch.setattr(asyncio, "to_thread", fake_to_thread)
    provider = CapturingProvider(provider_name="openai", model_name="gpt-5-mini")
    state_store = FakeStateStore()
    state_store.conversations["conv-history"] = [
        ConversationMessage(role="user", content="第一句"),
        ConversationMessage(role="assistant", content="第一句回复"),
        ConversationMessage(role="user", content="第二句"),
        ConversationMessage(role="assistant", content="第二句回复"),
    ]
    service = AssistantService(
        provider_factory=lambda *_args, **_kwargs: provider,
        state_store=state_store,
        settings=Settings(),
        system_prompt_builder=lambda _message, _user_id=None, _stage_override=None: "SYSTEM",
    )

    result = await service.chat("第三句", conversation_id="conv-history", provider="openai", model="gpt-5-mini")

    assert provider.messages == [
        {"role": "system", "content": "SYSTEM"},
        {"role": "user", "content": "第一句"},
        {"role": "assistant", "content": "第一句回复"},
        {"role": "user", "content": "第二句"},
        {"role": "assistant", "content": "第二句回复"},
        {"role": "user", "content": "第三句"},
    ]
    assert result["debug"]["request_messages"] == provider.messages
    assert result["debug"]["history_messages_loaded"] == 4
    assert result["debug"]["history_messages_trimmed"] == 0
    assert result["debug"]["context_window_tokens"] == 400000


@pytest.mark.anyio
async def test_assistant_service_trims_history_by_model_context_budget(monkeypatch) -> None:
    async def fake_to_thread(func, *args, **kwargs):
        return func(*args, **kwargs)

    monkeypatch.setattr(asyncio, "to_thread", fake_to_thread)
    provider = CapturingProvider(provider_name="kimi", model_name="moonshot-v1-8k")
    state_store = FakeStateStore()
    long_text = "a" * 5000
    state_store.conversations["conv-trim"] = [
        ConversationMessage(role="user", content=long_text),
        ConversationMessage(role="assistant", content=long_text),
        ConversationMessage(role="user", content=long_text),
        ConversationMessage(role="assistant", content=long_text),
    ]
    service = AssistantService(
        provider_factory=lambda *_args, **_kwargs: provider,
        state_store=state_store,
        settings=Settings(),
        system_prompt_builder=lambda _message, _user_id=None, _stage_override=None: "SYSTEM",
    )

    result = await service.chat(
        "当前问题",
        conversation_id="conv-trim",
        provider="kimi",
        model="moonshot-v1-8k",
    )

    assert provider.messages[0] == {"role": "system", "content": "SYSTEM"}
    assert provider.messages[-1] == {"role": "user", "content": "当前问题"}
    assert len(provider.messages) < 6
    assert result["debug"]["history_messages_trimmed"] > 0
    assert result["debug"]["history_messages_loaded"] < 4
