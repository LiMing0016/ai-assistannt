import json

import httpx
import pytest

from app.core.config import Settings
from app.providers.base import ProviderUsage
from app.providers.errors import ProviderHTTPError, ProviderTimeoutError
from app.providers.dashscope import DashScopeProvider
from app.providers.kimi import KimiProvider
from app.providers.openai import OpenAIProvider
from app.providers.openai_compatible import OpenAICompatibleProvider
from app.providers.registry import get_provider


def test_settings_default_provider_is_kimi() -> None:
    settings = Settings(_env_file=None)

    assert settings.default_provider == "kimi"
    assert settings.openai_base_url == "https://api.openai.com/v1"
    assert settings.openai_model == "gpt-5-mini"
    assert settings.openai_timeout_seconds == 30.0
    assert settings.kimi_base_url == "https://api.moonshot.cn/v1"
    assert settings.kimi_model == "moonshot-v1-8k"
    assert settings.kimi_timeout_seconds == 30.0
    assert settings.dashscope_base_url == "https://dashscope.aliyuncs.com/compatible-mode/v1"
    assert settings.dashscope_model == "qwen-plus"
    assert settings.dashscope_timeout_seconds == 30.0


def test_settings_can_override_kimi_environment(monkeypatch) -> None:
    monkeypatch.setenv("AI_ASSISTANT_DEFAULT_PROVIDER", "kimi")
    monkeypatch.setenv("AI_ASSISTANT_KIMI_API_KEY", "secret")
    monkeypatch.setenv("AI_ASSISTANT_KIMI_MODEL", "moonshot-v1-32k")
    monkeypatch.setenv("AI_ASSISTANT_KIMI_TIMEOUT_SECONDS", "45")
    monkeypatch.setenv("AI_ASSISTANT_OPENAI_MODEL", "gpt-5")
    monkeypatch.setenv("AI_ASSISTANT_OPENAI_TIMEOUT_SECONDS", "40")
    monkeypatch.setenv("AI_ASSISTANT_DASHSCOPE_MODEL", "qwen-max")
    monkeypatch.setenv("AI_ASSISTANT_DASHSCOPE_TIMEOUT_SECONDS", "50")

    settings = Settings(_env_file=None)

    assert settings.default_provider == "kimi"
    assert settings.kimi_api_key == "secret"
    assert settings.kimi_model == "moonshot-v1-32k"
    assert settings.kimi_timeout_seconds == 45.0
    assert settings.openai_model == "gpt-5"
    assert settings.openai_timeout_seconds == 40.0
    assert settings.dashscope_model == "qwen-max"
    assert settings.dashscope_timeout_seconds == 50.0


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


@pytest.mark.anyio
async def test_openai_provider_parses_chat_completion_response() -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        payload = json.loads(request.content.decode("utf-8"))
        assert request.url == httpx.URL("https://api.openai.com/v1/chat/completions")
        assert request.headers["Authorization"] == "Bearer secret"
        assert payload["model"] == "gpt-5-mini"
        return httpx.Response(
            200,
            json={
                "usage": {
                    "prompt_tokens": 100,
                    "completion_tokens": 20,
                    "total_tokens": 120,
                    "prompt_tokens_details": {
                        "cached_tokens": 60,
                    },
                },
                "choices": [
                    {
                        "message": {
                            "role": "assistant",
                            "content": "OpenAI reply",
                        }
                    }
                ],
            },
        )

    transport = httpx.MockTransport(handler)
    provider = OpenAIProvider(
        api_key="secret",
        base_url="https://api.openai.com/v1",
        model="gpt-5-mini",
        transport=transport,
    )

    result = await provider.generate([{"role": "user", "content": "hello"}])

    assert result.provider == "openai"
    assert result.model == "gpt-5-mini"
    assert result.reply == "OpenAI reply"
    assert result.usage == ProviderUsage(
        prompt_tokens=100,
        completion_tokens=20,
        total_tokens=120,
        cached_tokens=60,
    )


@pytest.mark.anyio
async def test_dashscope_provider_parses_chat_completion_response() -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        payload = json.loads(request.content.decode("utf-8"))
        assert request.url == httpx.URL(
            "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
        )
        assert request.headers["Authorization"] == "Bearer secret"
        assert payload["model"] == "qwen-plus"
        return httpx.Response(
            200,
            json={
                "choices": [
                    {
                        "message": {
                            "role": "assistant",
                            "content": "DashScope reply",
                        }
                    }
                ],
            },
        )

    transport = httpx.MockTransport(handler)
    provider = DashScopeProvider(
        api_key="secret",
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        model="qwen-plus",
        transport=transport,
    )

    result = await provider.generate([{"role": "user", "content": "hello"}])

    assert result.provider == "dashscope"
    assert result.model == "qwen-plus"
    assert result.reply == "DashScope reply"


@pytest.mark.anyio
async def test_provider_raises_timeout_error_when_upstream_times_out() -> None:
    async def handler(_request: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout("timed out")

    provider = KimiProvider(
        api_key="secret",
        base_url="https://api.moonshot.cn/v1",
        model="moonshot-v1-8k",
        transport=httpx.MockTransport(handler),
    )

    with pytest.raises(ProviderTimeoutError):
        await provider.generate([{"role": "user", "content": "hello"}])


@pytest.mark.anyio
async def test_provider_raises_http_error_with_status_and_message() -> None:
    async def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            401,
            json={"error": {"message": "Invalid API key"}},
        )

    provider = OpenAIProvider(
        api_key="secret",
        base_url="https://api.openai.com/v1",
        model="gpt-5-mini",
        transport=httpx.MockTransport(handler),
    )

    with pytest.raises(ProviderHTTPError) as exc_info:
        await provider.generate([{"role": "user", "content": "hello"}])

    assert exc_info.value.status_code == 401
    assert "Invalid API key" in exc_info.value.message


def test_all_providers_share_openai_compatible_base() -> None:
    assert issubclass(KimiProvider, OpenAICompatibleProvider)
    assert issubclass(OpenAIProvider, OpenAICompatibleProvider)
    assert issubclass(DashScopeProvider, OpenAICompatibleProvider)


def test_provider_registry_returns_kimi_provider() -> None:
    settings = Settings(
        default_provider="kimi",
        kimi_api_key="secret",
        kimi_timeout_seconds=42.0,
    )

    provider = get_provider(settings)

    assert isinstance(provider, KimiProvider)
    assert provider._timeout_seconds == 42.0


def test_provider_registry_returns_openai_provider() -> None:
    settings = Settings(
        default_provider="openai",
        openai_api_key="secret",
        openai_timeout_seconds=41.0,
    )

    provider = get_provider(settings)

    assert isinstance(provider, OpenAIProvider)
    assert provider._timeout_seconds == 41.0


def test_provider_registry_returns_dashscope_provider() -> None:
    settings = Settings(
        default_provider="dashscope",
        dashscope_api_key="secret",
        dashscope_timeout_seconds=39.0,
    )

    provider = get_provider(settings)

    assert isinstance(provider, DashScopeProvider)
    assert provider._timeout_seconds == 39.0
