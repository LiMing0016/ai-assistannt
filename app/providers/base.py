from typing import Protocol

from pydantic import BaseModel


class ChatMessage(BaseModel):
    role: str
    content: str


class ProviderResponse(BaseModel):
    provider: str
    model: str
    reply: str


class ChatProvider(Protocol):
    async def generate(self, messages: list[ChatMessage | dict[str, str]]) -> ProviderResponse: ...
