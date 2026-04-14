import json

from redis import Redis

from app.profile.models import TranslationProfileSnapshot
from app.state.models import (
    ConversationMessage,
    ConversationPreference,
    ConversationState,
    TaskState,
)


class RedisStateStore:
    def __init__(self, redis_url: str, client: Redis | None = None) -> None:
        self._redis_url = redis_url
        self._client = client
        if self._client is None and redis_url:
            self._client = Redis.from_url(redis_url, decode_responses=True)

    def is_enabled(self) -> bool:
        return bool(self._redis_url and self._client is not None)

    @property
    def client(self) -> Redis | None:
        return self._client

    def append_conversation_messages(
        self,
        conversation_id: str,
        messages: list[ConversationMessage],
    ) -> None:
        if not self.is_enabled():
            return
        key = f"ai-assistant:conversation:{conversation_id}"
        payloads = [message.model_dump_json() for message in messages]
        if payloads:
            self._client.rpush(key, *payloads)

    def load_conversation_state(self, conversation_id: str) -> ConversationState:
        if not self.is_enabled():
            return ConversationState(conversation_id=conversation_id, messages=[])
        key = f"ai-assistant:conversation:{conversation_id}"
        values = self._client.lrange(key, 0, -1)
        messages = [ConversationMessage.model_validate_json(value) for value in values]
        return ConversationState(conversation_id=conversation_id, messages=messages)

    def save_conversation_preference(self, preference: ConversationPreference) -> None:
        if not self.is_enabled():
            return
        key = f"ai-assistant:conversation-preference:{preference.conversation_id}"
        self._client.set(key, preference.model_dump_json())

    def load_conversation_preference(
        self,
        conversation_id: str,
    ) -> ConversationPreference | None:
        if not self.is_enabled():
            return None
        key = f"ai-assistant:conversation-preference:{conversation_id}"
        value = self._client.get(key)
        if not value:
            return None
        return ConversationPreference.model_validate(json.loads(value))

    def save_task_state(self, task_state: TaskState) -> None:
        if not self.is_enabled():
            return
        key = f"ai-assistant:task:{task_state.task_id}"
        self._client.set(key, task_state.model_dump_json())

    def load_task_state(self, task_id: str) -> TaskState | None:
        if not self.is_enabled():
            return None
        key = f"ai-assistant:task:{task_id}"
        value = self._client.get(key)
        if not value:
            return None
        return TaskState.model_validate(json.loads(value))

    def save_translation_profile(self, profile: TranslationProfileSnapshot) -> None:
        if not self.is_enabled():
            return
        key = f"ai-assistant:translation-profile:{profile.learner_id}"
        self._client.set(key, profile.model_dump_json())

    def load_translation_profile(self, learner_id: str) -> TranslationProfileSnapshot | None:
        if not self.is_enabled():
            return None
        key = f"ai-assistant:translation-profile:{learner_id}"
        value = self._client.get(key)
        if not value:
            return None
        return TranslationProfileSnapshot.model_validate(json.loads(value))
