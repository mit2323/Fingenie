from fastapi import APIRouter, Depends

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.database.session import get_db

from app.models.user import User

from app.repositories.holding_repository import HoldingRepository
from app.repositories.portfolio_repository import PortfolioRepository

from app.schemas.portfolio_summary import PortfolioSummaryResponse

from app.services.analytics.portfolio_summary_service import (
    PortfolioSummaryService,
)

router = APIRouter(
    prefix="/portfolio-summary",
    tags=["Portfolio Summary"],
)


def get_summary_service(
    db: AsyncSession = Depends(get_db),
):

    holding_repository = HoldingRepository(db)

    portfolio_repository = PortfolioRepository(db)

    return PortfolioSummaryService(
        holding_repository,
        portfolio_repository,
    )


@router.get(
    "/{portfolio_id}",
    response_model=PortfolioSummaryResponse,
)
async def get_summary(
    portfolio_id: int,
    current_user: User = Depends(get_current_user),
    service: PortfolioSummaryService = Depends(
        get_summary_service
    ),
):

    return await service.get_summary(
        portfolio_id,
        current_user.id,
    )