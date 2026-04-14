from pydantic import BaseModel, Field

from app.schemas.translation import TranslationStage


class AgentExecuteRequest(BaseModel):
    message: str = Field(min_length=1)


class AssistantChatRequest(BaseModel):
    message: str = Field(min_length=1)
    conversation_id: str | None = None
    user_id: str | None = None
    stage: TranslationStage | None = None
    provider: str | None = None
    model: str | None = None


class AgentStateMetadata(BaseModel):
    conversation_enabled: bool
    task_state_enabled: bool


class AssistantDebugMetadata(BaseModel):
    loaded_skills: list[str] = Field(default_factory=list)
    resolved_stage: TranslationStage | None = None
    stage_source: str = "none"
    loaded_stage_context: bool = False
    history_messages_loaded: int = 0
    history_messages_trimmed: int = 0
    context_window_tokens: int = 0
    input_budget_tokens: int = 0
    estimated_input_tokens: int = 0
    system_prompt: str
    request_messages: list[dict[str, str]] = Field(default_factory=list)


class AssistantUsageMetadata(BaseModel):
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    cached_tokens: int = 0
    cache_hit_ratio: float = 0.0


class AgentExecuteResponse(BaseModel):
    reply: str
    processor: str
    tool: str
    trace_id: str
    tracing: dict[str, object]
    state: AgentStateMetadata


class AssistantChatResponse(BaseModel):
    reply: str
    provider: str
    model: str
    processor: str
    trace_id: str
    tracing: dict[str, object]
    state: AgentStateMetadata
    debug: AssistantDebugMetadata
    usage: AssistantUsageMetadata
