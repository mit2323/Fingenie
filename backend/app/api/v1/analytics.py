from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.database.session import get_db

from app.models.user import User

from app.repositories.holding_repository import HoldingRepository
from app.repositories.portfolio_repository import PortfolioRepository

from app.schemas.allocation import SectorAllocationResponse

from app.services.analytics.allocation_service import AllocationService

router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"],
)


def get_allocation_service(
    db: AsyncSession = Depends(get_db),
):

    holding_repository = HoldingRepository(db)

    portfolio_repository = PortfolioRepository(db)

    return AllocationService(
        holding_repository,
        portfolio_repository,
    )


@router.get(
    "/sector-allocation/{portfolio_id}",
    response_model=list[SectorAllocationResponse],
)
async def get_sector_allocation(
    portfolio_id: int,
    current_user: User = Depends(get_current_user),
    service: AllocationService = Depends(
        get_allocation_service,
    ),
):

    return await service.get_sector_allocation(
        portfolio_id,
        current_user.id,
    )