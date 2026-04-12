from app.core.config import Settings
from app.providers.kimi import KimiProvider


def get_provider(settings: Settings):
    if settings.default_provider == "kimi":
        return KimiProvider(
            api_key=settings.kimi_api_key,
            base_url=settings.kimi_base_url,
            model=settings.kimi_model,
        )
    raise ValueError(f"Unsupported provider: {settings.default_provider}")
