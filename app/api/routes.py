from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse

from app.core.dependencies import get_agent_graph_service, get_assistant_service, get_translation_service
from app.graphs.agent_graph import AgentGraphService
from app.integrations.errors import BackendHTTPError, BackendTimeoutError
from app.providers.errors import ProviderHTTPError, ProviderNotSupportedError, ProviderTimeoutError
from app.schemas.agent import (
    AgentExecuteRequest,
    AgentExecuteResponse,
    AssistantChatRequest,
    AssistantChatResponse,
)
from app.services.assistant_service import AssistantService
from app.schemas.translation import TranslationRequest, TranslationResponse
from app.services.translation_service import TranslationService
from app.ui.chat_page import CHAT_PAGE_HTML


router = APIRouter()


@router.get("/health")
def health() -> dict[str, bool]:
    return {"ok": True}


@router.get("/chat", response_class=HTMLResponse)
def chat_page() -> HTMLResponse:
    return HTMLResponse(CHAT_PAGE_HTML)


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
    try:
        result = await assistant_service.chat(
            message=payload.message,
            conversation_id=payload.conversation_id,
            user_id=payload.user_id,
            stage=payload.stage,
            provider=payload.provider,
            model=payload.model,
        )
    except ProviderNotSupportedError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except ProviderTimeoutError as exc:
        raise HTTPException(status_code=504, detail=str(exc)) from exc
    except ProviderHTTPError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc

    return AssistantChatResponse(
        reply=result["reply"],
        provider=result["provider"],
        model=result["model"],
        processor=result["processor"],
        trace_id=str(uuid4()),
        tracing=result["tracing"],
        state=result["state"],
        debug=result["debug"],
        usage=result["usage"],
    )


@router.post("/translation/execute", response_model=TranslationResponse)
async def translation_execute(
    payload: TranslationRequest,
    translation_service: TranslationService = Depends(get_translation_service),
) -> TranslationResponse:
    try:
        return await translation_service.execute(payload)
    except BackendTimeoutError as exc:
        raise HTTPException(status_code=504, detail=str(exc)) from exc
    except BackendHTTPError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc
