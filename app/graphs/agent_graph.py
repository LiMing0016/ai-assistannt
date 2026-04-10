import asyncio
from typing import TypedDict

from langgraph.graph import END, START, StateGraph

from app.core.config import Settings
from app.observability.langsmith import build_tracing_metadata
from app.state.models import ConversationMessage
from app.state.redis_store import RedisStateStore
from app.tools.registry import get_registered_tools


class AgentState(TypedDict):
    message: str
    reply: str
    tool: str


class AgentGraphService:
    def __init__(self, backend_client, state_store: RedisStateStore, settings: Settings) -> None:
        self._settings = settings
        self._state_store = state_store
        self._tools = get_registered_tools(backend_client)
        self._graph = self._build_graph()

    def _build_graph(self):
        workflow = StateGraph(AgentState)
        workflow.add_node("respond", self._respond)
        workflow.add_edge(START, "respond")
        workflow.add_edge("respond", END)
        return workflow.compile()

    async def _respond(self, state: AgentState) -> AgentState:
        tool = self._tools["explain_english_knowledge"]
        result = await tool.execute(state["message"])
        return {
            "message": state["message"],
            "reply": result.reply,
            "tool": result.tool,
        }

    async def execute(self, message: str) -> dict[str, object]:
        result = await self._graph.ainvoke({"message": message, "reply": "", "tool": ""})
        if self._state_store.is_enabled():
            await asyncio.to_thread(
                self._state_store.append_conversation_messages,
                "default",
                [ConversationMessage(role="user", content=message)],
            )
        return {
            "reply": result["reply"],
            "processor": "langgraph",
            "tool": result["tool"],
            "tracing": build_tracing_metadata(self._settings),
            "state": {
                "conversation_enabled": self._state_store.is_enabled(),
                "task_state_enabled": self._state_store.is_enabled(),
            },
        }
