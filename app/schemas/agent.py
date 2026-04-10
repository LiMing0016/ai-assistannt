from pydantic import BaseModel, Field


class AgentExecuteRequest(BaseModel):
    message: str = Field(min_length=1)


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
