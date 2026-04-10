import asyncio

from app.integrations.backend_client import ExplainKnowledgeResponse
from app.tools.explain import ExplainEnglishKnowledgeTool


class FakeBackendClient:
    async def explain_english_knowledge(self, message: str) -> ExplainKnowledgeResponse:
        assert message == "What is present perfect?"
        return ExplainKnowledgeResponse(reply="Present perfect links past actions to the present.")


def test_explain_tool_delegates_to_backend_client() -> None:
    tool = ExplainEnglishKnowledgeTool(client=FakeBackendClient())

    result = asyncio.run(tool.execute("What is present perfect?"))

    assert result.tool == "explain_english_knowledge"
    assert result.reply == "Present perfect links past actions to the present."
