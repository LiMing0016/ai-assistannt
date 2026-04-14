import httpx

from app.providers.openai_compatible import OpenAICompatibleProvider


class KimiProvider(OpenAICompatibleProvider):
    name = "kimi"
