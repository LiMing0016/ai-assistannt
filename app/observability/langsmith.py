from app.core.config import Settings


def build_tracing_metadata(settings: Settings) -> dict[str, object]:
    return {
        "langsmith_enabled": settings.langsmith_enabled,
        "project": settings.langsmith_project if settings.langsmith_enabled else None,
    }
