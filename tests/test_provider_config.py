import json

import httpx
import pytest

from app.core.config import Settings
from app.providers.kimi import KimiProvider
from app.providers.registry import get_provider


def test_settings_default_provider_is_kimi() -> None:
    settings = Settings(_env_file=None)

    assert settings.default_provider == "kimi"
    assert settings.openai_base_url == "https://api.openai.com/v1"
    assert settings.openai_model == "gpt-5-mini"
    assert settings.kimi_base_url == "https://api.moonshot.cn/v1"
    assert settings.kimi_model == "moonshot-v1-8k"
    assert settings.dashscope_base_url == "https://dashscope.aliyuncs.com/compatible-mode/v1"
    assert settings.dashscope_model == "qwen-plus"


def test_settings_can_override_kimi_environment(monkeypatch) -> None:
    monkeypatch.setenv("AI_ASSISTANT_DEFAULT_PROVIDER", "kimi")
    monkeypatch.setenv("AI_ASSISTANT_KIMI_API_KEY", "secret")
    monkeypatch.setenv("AI_ASSISTANT_KIMI_MODEL", "moonshot-v1-32k")
    monkeypatch.setenv("AI_ASSISTANT_OPENAI_MODEL", "gpt-5")
    monkeypatch.setenv("AI_ASSISTANT_DASHSCOPE_MODEL", "qwen-max")

    settings = Settings(_env_file=None)

    assert settings.default_provider == "kimi"
    assert settings.kimi_api_key == "secret"
    assert settings.kimi_model == "moonshot-v1-32k"
    assert settings.openai_model == "gpt-5"
    assert settings.dashscope_model == "qwen-max"


@pytest.mark.anyio
async def test_kimi_provider_parses_chat_completion_response() -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        payload = json.loads(request.content.decode("utf-8"))
        assert request.url == httpx.URL("https://api.moonshot.cn/v1/chat/completions")
        assert request.headers["Authorization"] == "Bearer secret"
        assert payload["model"] == "moonshot-v1-8k"
        assert payload["messages"] == [{"role": "user", "content": "hello"}]
        return httpx.Response(
            200,
            json={
                "id": "chatcmpl-1",
                "choices": [
                    {
                        "message": {
                            "role": "assistant",
                            "content": "你好，我是 Kimi。",
                        }
                    }
                ],
            },
        )

    transport = httpx.MockTransport(handler)
    provider = KimiProvider(
        api_key="secret",
        base_url="https://api.moonshot.cn/v1",
        model="moonshot-v1-8k",
        transport=transport,
    )

    result = await provider.generate([{"role": "user", "content": "hello"}])

    assert result.provider == "kimi"
    assert result.model == "moonshot-v1-8k"
    assert result.reply == "你好，我是 Kimi。"


def test_provider_registry_returns_kimi_provider() -> None:
    settings = Settings(
        default_provider="kimi",
        kimi_api_key="secret",
    )

    provider = get_provider(settings)

    assert isinstance(provider, KimiProvider)
