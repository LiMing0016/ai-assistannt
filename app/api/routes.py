from uuid import uuid4

from fastapi import APIRouter, Depends

from app.core.dependencies import get_agent_graph_service, get_assistant_service
from app.graphs.agent_graph import AgentGraphService
from app.schemas.agent import (
    AgentExecuteRequest,
    AgentExecuteResponse,
    AssistantChatRequest,
    AssistantChatResponse,
)
from app.services.assistant_service import AssistantService


router = APIRouter()


@router.get("/health")
def health() -> dict[str, bool]:
    return {"ok": True}


@router.post("/agent/execute", response_model=AgentExecuteResponse)
async def agent_execute(
    payload: AgentExecuteRequest,
    graph_service: AgentGraphService = Depends(get_agent_graph_service),
) -> AgentExecuteResponse:
    result = await graph_service.execute(payload.message)
    return AgentExecuteResponse(
        reply=result["reply"],
        processor=result["processor"],
        tool=result["tool"],
        trace_id=str(uuid4()),
        tracing=result["tracing"],
        state=result["state"],
    )


@router.post("/assistant/chat", response_model=AssistantChatResponse)
async def assistant_chat(
    payload: AssistantChatRequest,
    assistant_service: AssistantService = Depends(get_assistant_service),
) -> AssistantChatResponse:
    result = await assistant_service.chat(
        message=payload.message,
        conversation_id=payload.conversation_id,
    )
    return AssistantChatResponse(
        reply=result["reply"],
        provider=result["provider"],
        model=result["model"],
        processor=result["processor"],
        trace_id=str(uuid4()),
        tracing=result["tracing"],
        state=result["state"],
    )
