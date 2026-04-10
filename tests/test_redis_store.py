from app.state.models import ConversationMessage, TaskState
from app.state.redis_store import RedisStateStore


class FakeRedis:
    def __init__(self) -> None:
        self.values: dict[str, object] = {}

    def rpush(self, key: str, *values: str) -> None:
        self.values.setdefault(key, [])
        self.values[key].extend(values)

    def lrange(self, key: str, start: int, end: int) -> list[str]:
        data = list(self.values.get(key, []))
        if end == -1:
            return data[start:]
        return data[start : end + 1]

    def set(self, key: str, value: str) -> None:
        self.values[key] = value

    def get(self, key: str) -> str | None:
        value = self.values.get(key)
        return value if isinstance(value, str) else None


def test_redis_store_can_append_and_load_conversation_state() -> None:
    store = RedisStateStore(redis_url="redis://unused", client=FakeRedis())

    store.append_conversation_messages(
        "conv-1",
        [ConversationMessage(role="user", content="Hello")],
    )

    state = store.load_conversation_state("conv-1")

    assert [message.content for message in state.messages] == ["Hello"]


def test_redis_store_can_save_and_load_task_state() -> None:
    store = RedisStateStore(redis_url="redis://unused", client=FakeRedis())
    task = TaskState(task_id="task-1", status="queued", task_type="explain")

    store.save_task_state(task)

    loaded = store.load_task_state("task-1")

    assert loaded is not None
    assert loaded.task_id == "task-1"
    assert loaded.status == "queued"
