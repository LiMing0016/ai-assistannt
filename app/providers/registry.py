from app.core.config import Settings
from app.providers.dashscope import DashScopeProvider
from app.providers.errors import ProviderNotSupportedError
from app.providers.kimi import KimiProvider
from app.providers.openai import OpenAIProvider


def get_provider(
    settings: Settings,
    provider_name: str | None = None,
    model_name: str | None = None,
):
    selected_provider = provider_name or settings.default_provider

    if selected_provider == "kimi":
        return KimiProvider(
            api_key=settings.kimi_api_key,
            base_url=settings.kimi_base_url,
            model=model_name or settings.kimi_model,
            timeout_seconds=settings.kimi_timeout_seconds,
        )
    if selected_provider == "openai":
        return OpenAIProvider(
            api_key=settings.openai_api_key,
            base_url=settings.openai_base_url,
            model=model_name or settings.openai_model,
            timeout_seconds=settings.openai_timeout_seconds,
        )
    if selected_provider == "dashscope":
        return DashScopeProvider(
            api_key=settings.dashscope_api_key,
            base_url=settings.dashscope_base_url,
            model=model_name or settings.dashscope_model,
            timeout_seconds=settings.dashscope_timeout_seconds,
        )
    raise ProviderNotSupportedError(f"Unsupported provider: {selected_provider}")
