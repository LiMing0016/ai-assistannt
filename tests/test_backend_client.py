import httpx
import pytest

from app.integrations.errors import BackendHTTPError, BackendTimeoutError
from app.integrations.backend_client import JavaBackendClient, MockBackendClient


@pytest.mark.anyio
async def test_backend_client_posts_to_configured_explain_endpoint() -> None:
    captured: dict[str, object] = {}

    async def handler(request: httpx.Request) -> httpx.Response:
        captured["url"] = str(request.url)
        captured["body"] = request.read().decode("utf-8")
        return httpx.Response(200, json={"reply": "Explained by backend."})

    transport = httpx.MockTransport(handler)
    client = JavaBackendClient(
        base_url="http://backend.test",
        timeout_seconds=5.0,
        explain_path="/api/internal/agent-tools/explain",
        transport=transport,
    )

    response = await client.explain_english_knowledge("What is a clause?")

    assert captured["url"] == "http://backend.test/api/internal/agent-tools/explain"
    assert '"message":"What is a clause?"' in captured["body"]
    assert response.reply == "Explained by backend."


@pytest.mark.anyio
async def test_backend_client_posts_to_configured_translate_endpoint() -> None:
    captured: dict[str, object] = {}

    async def handler(request: httpx.Request) -> httpx.Response:
        captured["url"] = str(request.url)
        captured["body"] = request.read().decode("utf-8")
        return httpx.Response(
            200,
            json={
                "standard_translation": "I went to the library yesterday.",
                "natural_translation": "I went to the library yesterday.",
            },
        )

    transport = httpx.MockTransport(handler)
    client = JavaBackendClient(
        base_url="http://backend.test",
        timeout_seconds=5.0,
        translate_path="/api/internal/agent-tools/translate",
        transport=transport,
    )

    response = await client.translate_text("我昨天去了图书馆。", "zh_to_en")

    assert captured["url"] == "http://backend.test/api/internal/agent-tools/translate"
    assert '"source_text":"我昨天去了图书馆。"' in captured["body"]
    assert '"direction":"zh_to_en"' in captured["body"]
    assert response.standard_translation == "I went to the library yesterday."
    assert response.natural_translation == "I went to the library yesterday."


@pytest.mark.anyio
async def test_backend_client_translate_raises_timeout_error() -> None:
    async def handler(_request: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout("timed out")

    client = JavaBackendClient(
        base_url="http://backend.test",
        timeout_seconds=5.0,
        translate_path="/api/internal/agent-tools/translate",
        transport=httpx.MockTransport(handler),
    )

    with pytest.raises(BackendTimeoutError):
        await client.translate_text("我昨天去了图书馆。", "zh_to_en")


@pytest.mark.anyio
async def test_backend_client_translate_raises_http_error() -> None:
    async def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(401, json={"message": "Unauthorized"})

    client = JavaBackendClient(
        base_url="http://backend.test",
        timeout_seconds=5.0,
        translate_path="/api/internal/agent-tools/translate",
        transport=httpx.MockTransport(handler),
    )

    with pytest.raises(BackendHTTPError) as exc_info:
        await client.translate_text("我昨天去了图书馆。", "zh_to_en")

    assert exc_info.value.status_code == 401
    assert exc_info.value.message == "Unauthorized"


@pytest.mark.anyio
async def test_mock_backend_client_returns_stubbed_translate_response() -> None:
    client = MockBackendClient()

    response = await client.translate_text("我昨天去了图书馆。", "zh_to_en")

    assert response.standard_translation == "I went to the library yesterday."
    assert response.natural_translation == "I went to the library yesterday."


@pytest.mark.anyio
async def test_mock_backend_client_returns_stubbed_explain_response() -> None:
    client = MockBackendClient()

    response = await client.explain_english_knowledge("What is present perfect?")

    assert "present perfect" in response.reply.lower()
