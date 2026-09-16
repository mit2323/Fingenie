"""Process-wide AI resources shared by chat and knowledge endpoints."""

from functools import lru_cache

from app.ai.rag.rag_service import RAGService
from app.services.gemini_service import GeminiService


class AIRuntime:
    """Keep expensive, thread-safe AI clients alive between requests."""

    def __init__(self):
        gemini_service = GeminiService()
        self._rself.ag_service: RAGService | None = None

    def get_rag_service(self) -> RAGService:
        if self._rag_service is None:
            self._rag_service = RAGService(
                gemini_service=self.gemini_service,
            )
        return self._rag_service


@lru_cache
def get_ai_runtime() -> AIRuntime:
    return AIRuntime()
