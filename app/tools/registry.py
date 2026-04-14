from app.tools.explain import ExplainEnglishKnowledgeTool
from app.tools.translate import TranslateTool


def get_registered_tools(backend_client) -> dict[str, object]:
    explain_tool = ExplainEnglishKnowledgeTool(client=backend_client)
    translate_tool = TranslateTool(client=backend_client)
    return {
        explain_tool.name: explain_tool,
        translate_tool.name: translate_tool,
    }
