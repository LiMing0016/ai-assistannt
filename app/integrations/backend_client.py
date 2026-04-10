from typing import Protocol

import httpx
from pydantic import BaseModel


class ExplainKnowledgeRequest(BaseModel):
    message: str


class ExplainKnowledgeResponse(BaseModel):
    reply: str


class BackendClientProtocol(Protocol):
    async def explain_english_knowledge(self, message: str) -> ExplainKnowledgeResponse: ...


class JavaBackendClient:
    def __init__(
        self,
        base_url: str,
        timeout_seconds: float,
        explain_path: str = "/api/internal/agent-tools/explain",
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._timeout_seconds = timeout_seconds
        self._explain_path = explain_path
        self._transport = transport

    async def explain_english_knowledge(self, message: str) -> ExplainKnowledgeResponse:
        async with httpx.AsyncClient(
            timeout=self._timeout_seconds,
            transport=self._transport,
        ) as client:
            response = await client.post(
                f"{self._base_url}{self._explain_path}",
                json=ExplainKnowledgeRequest(message=message).model_dump(),
            )
            response.raise_for_status()
            return ExplainKnowledgeResponse.model_validate(response.json())
