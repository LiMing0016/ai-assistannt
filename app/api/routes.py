from uuid import uuid4

from fastapi import APIRouter, Depends

from app.core.dependencies import get_agent_graph_service
from app.graphs.agent_graph import AgentGraphService
from app.schemas.agent import AgentExecuteRequest, AgentExecuteResponse


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
