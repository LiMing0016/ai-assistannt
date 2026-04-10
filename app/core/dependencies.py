from functools import lru_cache

from fastapi import Depends

from app.core.config import Settings, settings
from app.graphs.agent_graph import AgentGraphService
from app.integrations.backend_client import BackendClientProtocol, JavaBackendClient
from app.state.redis_store import RedisStateStore


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return settings


@lru_cache(maxsize=1)
def get_backend_client() -> JavaBackendClient:
    current = get_settings()
    return JavaBackendClient(
        base_url=current.backend_base_url,
        timeout_seconds=current.backend_timeout_seconds,
        explain_path=current.backend_explain_path,
    )


@lru_cache(maxsize=1)
def get_state_store() -> RedisStateStore:
    return RedisStateStore(redis_url=get_settings().redis_url)


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
