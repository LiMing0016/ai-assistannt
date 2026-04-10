from pydantic import BaseModel

from app.integrations.backend_client import BackendClientProtocol


class ToolResult(BaseModel):
    tool: str
    reply: str


class ExplainEnglishKnowledgeTool:
    name = "explain_english_knowledge"

    def __init__(self, client: BackendClientProtocol) -> None:
        self._client = client

    async def execute(self, message: str) -> ToolResult:
        response = await self._client.explain_english_knowledge(message)
        return ToolResult(tool=self.name, reply=response.reply)
