import json

from redis import Redis

from app.state.models import ConversationMessage, ConversationState, TaskState


class RedisStateStore:
    def __init__(self, redis_url: str, client: Redis | None = None) -> None:
        self._redis_url = redis_url
        self._client = client or Redis.from_url(redis_url, decode_responses=True)

    def is_enabled(self) -> bool:
        return bool(self._redis_url)

    @property
    def client(self) -> Redis:
        return self._client

    def append_conversation_messages(
        self,
        conversation_id: str,
        messages: list[ConversationMessage],
    ) -> None:
        key = f"ai-assistant:conversation:{conversation_id}"
        payloads = [message.model_dump_json() for message in messages]
        if payloads:
            self._client.rpush(key, *payloads)

    def load_conversation_state(self, conversation_id: str) -> ConversationState:
        key = f"ai-assistant:conversation:{conversation_id}"
        values = self._client.lrange(key, 0, -1)
        messages = [ConversationMessage.model_validate_json(value) for value in values]
        return ConversationState(conversation_id=conversation_id, messages=messages)

    def save_task_state(self, task_state: TaskState) -> None:
        key = f"ai-assistant:task:{task_state.task_id}"
        self._client.set(key, task_state.model_dump_json())

    def load_task_state(self, task_id: str) -> TaskState | None:
        key = f"ai-assistant:task:{task_id}"
        value = self._client.get(key)
        if not value:
            return None
        return TaskState.model_validate(json.loads(value))
