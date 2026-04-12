import asyncio

from app.core.config import Settings
from app.observability.langsmith import build_tracing_metadata
from app.state.models import ConversationMessage
from app.state.redis_store import RedisStateStore


class AssistantService:
    def __init__(self, provider, state_store: RedisStateStore, settings: Settings) -> None:
        self._provider = provider
        self._state_store = state_store
        self._settings = settings

    async def chat(self, message: str, conversation_id: str | None = None) -> dict[str, object]:
        current_conversation_id = conversation_id or "default"
        provider_result = await self._provider.generate([{"role": "user", "content": message}])
        if self._state_store.is_enabled():
            await asyncio.to_thread(
                self._state_store.append_conversation_messages,
                current_conversation_id,
                [
                    ConversationMessage(role="user", content=message),
                    ConversationMessage(role="assistant", content=provider_result.reply),
                ],
            )
        return {
            "reply": provider_result.reply,
            "provider": provider_result.provider,
            "model": provider_result.model,
            "processor": "assistant",
            "tracing": build_tracing_metadata(self._settings),
            "state": {
                "conversation_enabled": self._state_store.is_enabled(),
                "task_state_enabled": self._state_store.is_enabled(),
            },
        }
