import json

import httpx

from app.providers.base import ChatMessage, ProviderResponse


class KimiProvider:
    name = "kimi"

    def __init__(
        self,
        api_key: str,
        base_url: str,
        model: str,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self._model = model
        self._transport = transport

    async def generate(self, messages: list[ChatMessage | dict[str, str]]) -> ProviderResponse:
        normalized_messages = [
            message.model_dump() if isinstance(message, ChatMessage) else message
            for message in messages
        ]
        async with httpx.AsyncClient(transport=self._transport) as client:
            response = await client.post(
                f"{self._base_url}/chat/completions",
                headers={"Authorization": f"Bearer {self._api_key}"},
                json={"model": self._model, "messages": normalized_messages},
            )
            response.raise_for_status()
        data = response.json()
        content = data["choices"][0]["message"]["content"]
        if isinstance(content, list):
            content = "".join(
                item.get("text", "")
                for item in content
                if isinstance(item, dict)
            )
        return ProviderResponse(provider=self.name, model=self._model, reply=str(content))
