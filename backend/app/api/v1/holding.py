from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.database.session import get_db

from app.models.user import User

from app.repositories.holding_repository import HoldingRepository
from app.repositories.portfolio_repository import PortfolioRepository
from app.repositories.stock_repository import StockRepository

from app.schemas.holding import (
    HoldingCreate,
    HoldingUpdate,
    HoldingResponse,
)

from app.services.stock_service import StockService
from app.services.holding_service import HoldingService


router = APIRouter(
    prefix="/holdings",
    tags=["Holdings"],
)


def get_holding_service(
    db: AsyncSession = Depends(get_db),
) -> HoldingService:

    holding_repository = HoldingRepository(db)

    portfolio_repository = PortfolioRepository(db)

    stock_repository = StockRepository(db)

    stock_service = StockService(stock_repository)

    return HoldingService(
        holding_repository=holding_repository,
        portfolio_repository=portfolio_repository,
        stock_service=stock_service,
    )


@router.post(
    "",
    response_model=HoldingResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_holding(
    request: HoldingCreate,
    current_user: User = Depends(get_current_user),
    service: HoldingService = Depends(get_holding_service),
):
    return await service.create_holding(
        user_id=current_user.id,
        request=request,
    )


@router.get(
    "/{portfolio_id}",
    response_model=list[HoldingResponse],
)
async def get_holdings(
    portfolio_id: int,
    current_user: User = Depends(get_current_user),
    service: HoldingService = Depends(get_holding_service),
):
    return await service.get_holdings(
        portfolio_id=portfolio_id,
        user_id=current_user.id,
    )


@router.put(
    "/{holding_id}",
    response_model=HoldingResponse,
)
async def update_holding(
    holding_id: int,
    request: HoldingUpdate,
    current_user: User = Depends(get_current_user),
    service: HoldingService = Depends(get_holding_service),
):
    return await service.update_holding(
        holding_id=holding_id,
        user_id=current_user.id,
        request=request,
    )


@router.delete(
    "/{holding_id}",
    status_code=status.HTTP_200_OK,
)
async def delete_holding(
    holding_id: int,
    current_user: User = Depends(get_current_user),
    service: HoldingService = Depends(get_holding_service),
):
    return await service.delete_holding(
        holding_id=holding_id,
        user_id=current_user.id,
    )