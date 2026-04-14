from typing import Protocol

from pydantic import BaseModel


class ChatMessage(BaseModel):
    role: str
    content: str


class ProviderUsage(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    cached_tokens: int = 0


class ProviderResponse(BaseModel):
    provider: str
    model: str
    reply: str
    usage: ProviderUsage | None = None


class ChatProvider(Protocol):
    async def generate(self, messages: list[ChatMessage | dict[str, str]]) -> ProviderResponse: ...
