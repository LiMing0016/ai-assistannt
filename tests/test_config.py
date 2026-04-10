from app.core.config import Settings


def test_settings_defaults_cover_integrations() -> None:
    settings = Settings()

    assert settings.backend_base_url == "http://127.0.0.1:8080"
    assert settings.backend_timeout_seconds == 5.0
    assert settings.backend_explain_path == "/api/internal/agent-tools/explain"
    assert settings.redis_url == "redis://127.0.0.1:6379/0"
    assert settings.langsmith_enabled is False
    assert settings.langsmith_project == "ai-assistant"


def test_settings_can_read_environment_overrides(monkeypatch) -> None:
    monkeypatch.setenv("AI_ASSISTANT_BACKEND_BASE_URL", "http://127.0.0.1:18080")
    monkeypatch.setenv("AI_ASSISTANT_LANGSMITH_ENABLED", "true")

    settings = Settings()

    assert settings.backend_base_url == "http://127.0.0.1:18080"
    assert settings.langsmith_enabled is True
