from app.agents.english.translation_agent import TranslationAgent
from app.schemas.translation import TranslationRequest, TranslationResponse


class TranslationService:
    def __init__(self, agent: TranslationAgent) -> None:
        self._agent = agent

    async def execute(self, payload: TranslationRequest) -> TranslationResponse:
        return await self._agent.execute(payload)
