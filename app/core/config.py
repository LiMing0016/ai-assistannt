from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="AI_ASSISTANT_", extra="ignore")

    app_name: str = "ai-assistant"
    backend_base_url: str = "http://127.0.0.1:8080"
    backend_timeout_seconds: float = 5.0
    backend_explain_path: str = "/api/internal/agent-tools/explain"
    redis_url: str = "redis://127.0.0.1:6379/0"
    langsmith_enabled: bool = False
    langsmith_project: str = "ai-assistant"


settings = Settings()
