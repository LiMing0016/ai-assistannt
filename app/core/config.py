from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="AI_ASSISTANT_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "ai-assistant"
    default_provider: str = "kimi"
    backend_base_url: str = "http://127.0.0.1:8080"
    backend_timeout_seconds: float = 5.0
    backend_explain_path: str = "/api/internal/agent-tools/explain"
    openai_api_key: str = ""
    openai_base_url: str = "https://api.openai.com/v1"
    openai_model: str = "gpt-5-mini"
    kimi_api_key: str = ""
    kimi_base_url: str = "https://api.moonshot.cn/v1"
    kimi_model: str = "moonshot-v1-8k"
    dashscope_api_key: str = ""
    dashscope_base_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    dashscope_model: str = "qwen-plus"
    redis_url: str = "redis://127.0.0.1:6379/0"
    langsmith_enabled: bool = False
    langsmith_project: str = "ai-assistant"


settings = Settings()
