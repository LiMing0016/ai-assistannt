import httpx
import pytest

from app.integrations.backend_client import JavaBackendClient


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
