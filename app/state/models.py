from pydantic import BaseModel, Field


class ConversationMessage(BaseModel):
    role: str
    content: str


class ConversationState(BaseModel):
    conversation_id: str
    messages: list[ConversationMessage] = Field(default_factory=list)


class TaskState(BaseModel):
    task_id: str
    status: str
    task_type: str
    result: str | None = None
    error: str | None = None
