from pydantic import BaseModel, Field


class AgentExecuteRequest(BaseModel):
    message: str = Field(min_length=1)


class AssistantChatRequest(BaseModel):
    message: str = Field(min_length=1)
    conversation_id: str | None = None


class AgentStateMetadata(BaseModel):
    conversation_enabled: bool
    task_state_enabled: bool


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
