from typing import Protocol

import httpx
from pydantic import BaseModel

from app.integrations.errors import BackendHTTPError, BackendTimeoutError


class ExplainKnowledgeRequest(BaseModel):
    message: str


class ExplainKnowledgeResponse(BaseModel):
    reply: str


class TranslateTextRequest(BaseModel):
    source_text: str
    direction: str


class TranslateTextResponse(BaseModel):
    standard_translation: str
    natural_translation: str


class BackendClientProtocol(Protocol):
    async def explain_english_knowledge(self, message: str) -> ExplainKnowledgeResponse: ...
    async def translate_text(self, source_text: str, direction: str) -> TranslateTextResponse: ...


class JavaBackendClient:
    def __init__(
        self,
        base_url: str,
        timeout_seconds: float,
        explain_path: str = "/api/internal/agent-tools/explain",
        translate_path: str = "/api/internal/agent-tools/translate",
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._timeout_seconds = timeout_seconds
        self._explain_path = explain_path
        self._translate_path = translate_path
        self._transport = transport

    async def explain_english_knowledge(self, message: str) -> ExplainKnowledgeResponse:
        async with httpx.AsyncClient(
            timeout=self._timeout_seconds,
            transport=self._transport,
        ) as client:
            try:
                response = await client.post(
                    f"{self._base_url}{self._explain_path}",
                    json=ExplainKnowledgeRequest(message=message).model_dump(),
                )
                response.raise_for_status()
                return ExplainKnowledgeResponse.model_validate(response.json())
            except httpx.ReadTimeout as exc:
                raise BackendTimeoutError("backend explain request timed out") from exc
            except httpx.HTTPStatusError as exc:
                raise BackendHTTPError(
                    status_code=exc.response.status_code,
                    message=_extract_error_message(exc.response),
                ) from exc

    async def translate_text(self, source_text: str, direction: str) -> TranslateTextResponse:
        async with httpx.AsyncClient(
            timeout=self._timeout_seconds,
            transport=self._transport,
        ) as client:
            try:
                response = await client.post(
                    f"{self._base_url}{self._translate_path}",
                    json=TranslateTextRequest(source_text=source_text, direction=direction).model_dump(),
                )
                response.raise_for_status()
                return TranslateTextResponse.model_validate(response.json())
            except httpx.ReadTimeout as exc:
                raise BackendTimeoutError("backend translate request timed out") from exc
            except httpx.HTTPStatusError as exc:
                raise BackendHTTPError(
                    status_code=exc.response.status_code,
                    message=_extract_error_message(exc.response),
                ) from exc


def _extract_error_message(response: httpx.Response) -> str:
    try:
        data = response.json()
    except ValueError:
        return f"backend service error ({response.status_code})"

    if isinstance(data, dict):
        message = data.get("message")
        if isinstance(message, str) and message:
            return message
        error = data.get("error")
        if isinstance(error, dict):
            nested_message = error.get("message")
            if isinstance(nested_message, str) and nested_message:
                return nested_message

    return f"backend service error ({response.status_code})"


class MockBackendClient:
    async def explain_english_knowledge(self, message: str) -> ExplainKnowledgeResponse:
        return ExplainKnowledgeResponse(
            reply=(
                f"Mock explain result: `{message}` is treated as an English knowledge query. "
                "Present perfect usually connects a past action with the present."
            )
        )

    async def translate_text(self, source_text: str, direction: str) -> TranslateTextResponse:
        if direction == "zh_to_en":
            if source_text == "我昨天去了图书馆。":
                translated = "I went to the library yesterday."
            else:
                translated = f"[mock zh_to_en] {source_text}"
        else:
            if source_text == "I went to the library yesterday.":
                translated = "我昨天去了图书馆。"
            else:
                translated = f"[mock en_to_zh] {source_text}"
        return TranslateTextResponse(
            standard_translation=translated,
            natural_translation=translated,
        )
