import httpx

from app.providers.base import ChatMessage, ProviderResponse, ProviderUsage
from app.providers.errors import ProviderHTTPError, ProviderTimeoutError


class OpenAICompatibleProvider:
    name = "openai-compatible"

    def __init__(
        self,
        api_key: str,
        base_url: str,
        model: str,
        timeout_seconds: float = 30.0,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self._model = model
        self._timeout_seconds = timeout_seconds
        self._transport = transport

    async def generate(self, messages: list[ChatMessage | dict[str, str]]) -> ProviderResponse:
        normalized_messages = [
            message.model_dump() if isinstance(message, ChatMessage) else message
            for message in messages
        ]
        async with httpx.AsyncClient(
            transport=self._transport,
            timeout=self._timeout_seconds,
        ) as client:
            try:
                response = await client.post(
                    f"{self._base_url}/chat/completions",
                    headers={"Authorization": f"Bearer {self._api_key}"},
                    json={"model": self._model, "messages": normalized_messages},
                )
                response.raise_for_status()
            except httpx.ReadTimeout as exc:
                raise ProviderTimeoutError("provider request timed out") from exc
            except httpx.HTTPStatusError as exc:
                message = _extract_error_message(exc.response)
                raise ProviderHTTPError(status_code=exc.response.status_code, message=message) from exc
        data = response.json()
        content = data["choices"][0]["message"]["content"]
        if isinstance(content, list):
            content = "".join(
                item.get("text", "")
                for item in content
                if isinstance(item, dict)
            )
        return ProviderResponse(
            provider=self.name,
            model=self._model,
            reply=str(content),
            usage=_parse_usage(data.get("usage")),
        )


def _extract_error_message(response: httpx.Response) -> str:
    try:
        data = response.json()
    except ValueError:
        return f"upstream provider error ({response.status_code})"

    if isinstance(data, dict):
        error = data.get("error")
        if isinstance(error, dict):
            message = error.get("message")
            if isinstance(message, str) and message:
                return message
        message = data.get("message")
        if isinstance(message, str) and message:
            return message

    return f"upstream provider error ({response.status_code})"


def _parse_usage(raw_usage: object) -> ProviderUsage | None:
    if not isinstance(raw_usage, dict):
        return None

    prompt_tokens = _safe_int(raw_usage.get("prompt_tokens"))
    completion_tokens = _safe_int(raw_usage.get("completion_tokens"))
    total_tokens = _safe_int(raw_usage.get("total_tokens"))
    prompt_tokens_details = raw_usage.get("prompt_tokens_details")
    cached_tokens = 0
    if isinstance(prompt_tokens_details, dict):
        cached_tokens = _safe_int(prompt_tokens_details.get("cached_tokens"))

    return ProviderUsage(
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        total_tokens=total_tokens,
        cached_tokens=cached_tokens,
    )


def _safe_int(value: object) -> int:
    if isinstance(value, int):
        return value
    return 0
