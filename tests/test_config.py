from pathlib import Path

from app.core.config import Settings


def test_settings_defaults_cover_integrations() -> None:
    settings = Settings(_env_file=None)

    assert settings.backend_base_url == "http://127.0.0.1:8080"
    assert settings.backend_timeout_seconds == 5.0
    assert settings.backend_explain_path == "/api/internal/agent-tools/explain"
    assert settings.redis_url == "redis://127.0.0.1:6379/0"
    assert settings.langsmith_enabled is False
    assert settings.langsmith_project == "ai-assistant"


def test_settings_can_read_environment_overrides(monkeypatch) -> None:
    monkeypatch.setenv("AI_ASSISTANT_BACKEND_BASE_URL", "http://127.0.0.1:18080")
    monkeypatch.setenv("AI_ASSISTANT_LANGSMITH_ENABLED", "true")

    settings = Settings(_env_file=None)

    assert settings.backend_base_url == "http://127.0.0.1:18080"
    assert settings.langsmith_enabled is True


def test_settings_can_read_dotenv_file() -> None:
    env_file = Path("tmp/test-config.env")
    env_file.parent.mkdir(parents=True, exist_ok=True)
    env_file.write_text(
        "\n".join(
            [
                "AI_ASSISTANT_DEFAULT_PROVIDER=kimi",
                "AI_ASSISTANT_KIMI_API_KEY=dotenv-secret",
                "AI_ASSISTANT_KIMI_MODEL=moonshot-v1-32k",
            ]
        ),
        encoding="utf-8",
    )

    settings = Settings(_env_file=env_file)

    assert settings.default_provider == "kimi"
    assert settings.kimi_api_key == "dotenv-secret"
    assert settings.kimi_model == "moonshot-v1-32k"
