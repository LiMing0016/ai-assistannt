from app.tools.explain import ExplainEnglishKnowledgeTool


def get_registered_tools(backend_client) -> dict[str, ExplainEnglishKnowledgeTool]:
    tool = ExplainEnglishKnowledgeTool(client=backend_client)
    return {tool.name: tool}
