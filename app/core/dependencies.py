from functools import lru_cache

from fastapi import Depends

from app.core.config import Settings, settings
from app.graphs.agent_graph import AgentGraphService
from app.integrations.backend_client import BackendClientProtocol, JavaBackendClient, MockBackendClient
from app.agents.english.translation_agent import TranslationAgent
from app.prompting.loader import PromptLoader
from app.prompting.renderer import PromptRenderer
from app.profile.extractor.translation_signal_extractor import TranslationSignalExtractor
from app.profile.updater.translation_profile_updater import TranslationProfileUpdater
from app.providers.registry import get_provider
from app.services.assistant_service import AssistantService
from app.services.translation_service import TranslationService
from app.skills.context_builder import SkillContextBuilder
from app.state.redis_store import RedisStateStore
from app.tools.translate import TranslateTool


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return settings


@lru_cache(maxsize=1)
def get_backend_client() -> BackendClientProtocol:
    return build_backend_client(get_settings())


def build_backend_client(current: Settings) -> BackendClientProtocol:
    if current.backend_mode == "mock":
        return MockBackendClient()
    if current.backend_mode == "live":
        return JavaBackendClient(
            base_url=current.backend_base_url,
            timeout_seconds=current.backend_timeout_seconds,
            explain_path=current.backend_explain_path,
            translate_path=current.backend_translate_path,
        )
    raise ValueError(f"Unsupported backend mode: {current.backend_mode}")


@lru_cache(maxsize=1)
def get_state_store() -> RedisStateStore:
    return RedisStateStore(redis_url=get_settings().redis_url)


@lru_cache(maxsize=1)
def get_provider_factory():
    current = get_settings()

    def resolve(provider_name: str | None = None, model_name: str | None = None):
        return get_provider(current, provider_name=provider_name, model_name=model_name)

    return resolve


@lru_cache(maxsize=1)
def get_prompt_renderer() -> PromptRenderer:
    current = get_settings()
    return PromptRenderer(PromptLoader(base_dir=current.prompt_base_dir))


@lru_cache(maxsize=1)
def get_assistant_system_prompt() -> str:
    current = get_settings()
    loader = PromptLoader(base_dir=current.prompt_base_dir)
    return loader.load("assistant/system.md")


def get_assistant_skill_context_builder() -> SkillContextBuilder:
    current = get_settings()
    state_store = get_state_store()

    def resolve_stage(user_id: str) -> str | None:
        profile = state_store.load_translation_profile(user_id)
        if profile is None:
            return None
        return profile.current_stage

    return SkillContextBuilder(
        skills_base_dir=current.skill_base_dir,
        base_system_prompt=get_assistant_system_prompt(),
        stage_resolver=resolve_stage,
    )


def get_agent_graph_service(
    backend_client: BackendClientProtocol = Depends(get_backend_client),
    state_store: RedisStateStore = Depends(get_state_store),
    settings: Settings = Depends(get_settings),
) -> AgentGraphService:
    return AgentGraphService(
        backend_client=backend_client,
        state_store=state_store,
        settings=settings,
    )


def get_assistant_service(
    provider_factory=Depends(get_provider_factory),
    state_store: RedisStateStore = Depends(get_state_store),
    settings: Settings = Depends(get_settings),
    system_prompt_builder: SkillContextBuilder = Depends(get_assistant_skill_context_builder),
) -> AssistantService:
    return AssistantService(
        provider_factory=provider_factory,
        state_store=state_store,
        settings=settings,
        system_prompt_builder=system_prompt_builder.build,
    )


def get_translation_service(
    backend_client: BackendClientProtocol = Depends(get_backend_client),
    state_store: RedisStateStore = Depends(get_state_store),
    prompt_renderer: PromptRenderer = Depends(get_prompt_renderer),
) -> TranslationService:
    agent = TranslationAgent(
        translate_tool=TranslateTool(client=backend_client),
        signal_extractor=TranslationSignalExtractor(),
        profile_updater=TranslationProfileUpdater(state_store=state_store),
        prompt_renderer=prompt_renderer,
    )
    return TranslationService(agent=agent)
