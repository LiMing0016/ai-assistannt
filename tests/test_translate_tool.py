import asyncio

from app.integrations.backend_client import TranslateTextResponse
from app.tools.translate import TranslateTool


class FakeBackendClient:
    async def translate_text(self, source_text: str, direction: str) -> TranslateTextResponse:
        assert source_text == "我昨天去了图书馆。"
        assert direction == "zh_to_en"
        return TranslateTextResponse(
            standard_translation="I went to the library yesterday.",
            natural_translation="I went to the library yesterday.",
        )


def test_translate_tool_delegates_to_backend_client() -> None:
    tool = TranslateTool(client=FakeBackendClient())

    result = asyncio.run(tool.execute("我昨天去了图书馆。", "zh_to_en"))

    assert result.tool == "translate_text"
    assert result.standard_translation == "I went to the library yesterday."
    assert result.natural_translation == "I went to the library yesterday."
