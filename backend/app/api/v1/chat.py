from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.repositories.conversation_repository import (
    ConversationRepository,
)
from app.repositories.holding_repository import HoldingRepository
from app.repositories.portfolio_repository import PortfolioRepository

from app.schemas.chat import ChatRequest, ChatResponse

from app.services.analytics.allocation_service import AllocationService
from app.services.analytics.portfolio_summary_service import (
    PortfolioSummaryService,
)
from app.services.chat_service import ChatService
from app.services.market_data_service import MarketDataService
from app.services.ai_runtime import get_ai_runtime


router = APIRouter(
    prefix="/chat",
    tags=["AI Copilot"],
)


def get_chat_service(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> ChatService:

    holding_repository = HoldingRepository(db)

    portfolio_repository = PortfolioRepository(db)
    conversation_repository = ConversationRepository(db)
    portfolio_summary_service = PortfolioSummaryService(
        holding_repository=holding_repository,
        portfolio_repository=portfolio_repository,
    )

    allocation_service = AllocationService(
        holding_repository=holding_repository,
        portfolio_repository=portfolio_repository,
    )

    market_service = MarketDataService()

    ai_runtime = getattr(request.app.state, "ai_runtime", None)
    if ai_runtime is None:
        ai_runtime = get_ai_runtime()

    return ChatService(
        portfolio_summary_service=portfolio_summary_service,
        allocation_service=allocation_service,
        market_service=market_service,
        conversation_repository=conversation_repository,
        gemini_service=ai_runtime.gemini_service,
        rag_service_factory=ai_runtime.get_rag_service,
    )


@router.post(
    "",
    response_model=ChatResponse,
)
async def chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    service: ChatService = Depends(get_chat_service),
):

    return await service.chat(
        request=request,
        user_id=current_user.id,
    )
