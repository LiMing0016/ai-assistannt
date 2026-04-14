from pydantic import BaseModel

from app.integrations.backend_client import BackendClientProtocol


class TranslateToolResult(BaseModel):
    tool: str
    standard_translation: str
    natural_translation: str


class TranslateTool:
    name = "translate_text"

    def __init__(self, client: BackendClientProtocol) -> None:
        self._client = client

    async def execute(self, source_text: str, direction: str) -> TranslateToolResult:
        response = await self._client.translate_text(source_text, direction)
        return TranslateToolResult(
            tool=self.name,
            standard_translation=response.standard_translation,
            natural_translation=response.natural_translation,
        )
