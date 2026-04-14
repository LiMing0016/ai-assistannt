import asyncio
from collections.abc import Callable
from typing import Any

from app.core.config import Settings
from app.observability.langsmith import build_tracing_metadata
from app.state.models import ConversationMessage, ConversationPreference
from app.state.redis_store import RedisStateStore
from app.services.chat_context import build_chat_messages


SystemPromptBuilder = Callable[[str, str | None, str | None], str | dict[str, Any]]


class AssistantService:
    def __init__(
        self,
        provider_factory: Callable[[str | None, str | None], object],
        state_store: RedisStateStore,
        settings: Settings,
        system_prompt_builder: SystemPromptBuilder,
    ) -> None:
        self._provider_factory = provider_factory
        self._state_store = state_store
        self._settings = settings
        self._system_prompt_builder = system_prompt_builder

    async def chat(
        self,
        message: str,
        conversation_id: str | None = None,
        user_id: str | None = None,
        stage: str | None = None,
        provider: str | None = None,
        model: str | None = None,
    ) -> dict[str, object]:
        current_conversation_id = conversation_id or "default"
        resolved_provider = provider
        resolved_model = model

        if self._state_store.is_enabled() and not provider and not model:
            preference = await asyncio.to_thread(
                self._state_store.load_conversation_preference,
                current_conversation_id,
            )
            if preference is not None:
                resolved_provider = preference.provider
                resolved_model = preference.model

        prompt_context = self._system_prompt_builder(message, user_id, stage)
        if isinstance(prompt_context, str):
            debug = {
                "loaded_skills": [],
                "resolved_stage": None,
                "stage_source": "none",
                "loaded_stage_context": False,
                "history_messages_loaded": 0,
                "history_messages_trimmed": 0,
                "context_window_tokens": 0,
                "input_budget_tokens": 0,
                "estimated_input_tokens": 0,
                "system_prompt": prompt_context,
            }
            system_prompt = prompt_context
        else:
            debug = {
                "loaded_skills": prompt_context["loaded_skills"],
                "resolved_stage": prompt_context["resolved_stage"],
                "stage_source": prompt_context["stage_source"],
                "loaded_stage_context": prompt_context["loaded_stage_context"],
                "history_messages_loaded": 0,
                "history_messages_trimmed": 0,
                "context_window_tokens": 0,
                "input_budget_tokens": 0,
                "estimated_input_tokens": 0,
                "system_prompt": prompt_context["system_prompt"],
            }
            system_prompt = prompt_context["system_prompt"]
        chat_provider = self._provider_factory(resolved_provider, resolved_model)
        effective_provider = resolved_provider or getattr(chat_provider, "name", self._settings.default_provider)
        effective_model = resolved_model or getattr(chat_provider, "_model", "")

        history_messages: list[ConversationMessage] = []
        if self._state_store.is_enabled():
            conversation_state = await asyncio.to_thread(
                self._state_store.load_conversation_state,
                current_conversation_id,
            )
            history_messages = conversation_state.messages

        messages, context_debug = build_chat_messages(
            system_prompt=system_prompt,
            history_messages=history_messages,
            current_message=message,
            provider=effective_provider,
            model=effective_model,
        )
        debug.update(context_debug)
        debug["request_messages"] = messages

        provider_result = await chat_provider.generate(messages)

        if self._state_store.is_enabled() and (provider or model):
            await asyncio.to_thread(
                self._state_store.save_conversation_preference,
                ConversationPreference(
                    conversation_id=current_conversation_id,
                    provider=provider_result.provider,
                    model=provider_result.model,
                ),
            )

        if self._state_store.is_enabled():
            await asyncio.to_thread(
                self._state_store.append_conversation_messages,
                current_conversation_id,
                [
                    ConversationMessage(role="user", content=message),
                    ConversationMessage(role="assistant", content=provider_result.reply),
                ],
            )
        usage = provider_result.usage
        usage_payload = {
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0,
            "cached_tokens": 0,
            "cache_hit_ratio": 0.0,
        }
        if usage is not None:
            usage_payload = {
                "prompt_tokens": usage.prompt_tokens,
                "completion_tokens": usage.completion_tokens,
                "total_tokens": usage.total_tokens,
                "cached_tokens": usage.cached_tokens,
                "cache_hit_ratio": (
                    usage.cached_tokens / usage.prompt_tokens if usage.prompt_tokens else 0.0
                ),
            }
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
            "debug": debug,
            "usage": usage_payload,
        }
