from fastapi import APIRouter, Depends, status

from app.core.dependencies import (
    get_current_user,
    get_db,
)
from app.models.user import User
from app.repositories.portfolio_repository import PortfolioRepository
from app.schemas.portfolio import (
    PortfolioCreate,
    PortfolioResponse,
    PortfolioUpdate,
)
from app.services.portfolio_service import PortfolioService
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(
    prefix="/portfolios",
    tags=["Portfolios"],
)


def get_portfolio_service(
    db: AsyncSession = Depends(get_db),
):
    repository = PortfolioRepository(db)
    return PortfolioService(repository)


@router.post(
    "",
    response_model=PortfolioResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_portfolio(
    request: PortfolioCreate,
    current_user: User = Depends(get_current_user),
    service: PortfolioService = Depends(get_portfolio_service),
):
    return await service.create_portfolio(
        current_user.id,
        request,
    )


@router.get(
    "",
    response_model=list[PortfolioResponse],
)
async def get_all_portfolios(
    current_user: User = Depends(get_current_user),
    service: PortfolioService = Depends(get_portfolio_service),
):
    return await service.get_all_portfolios(
        current_user.id,
    )


@router.get(
    "/{portfolio_id}",
    response_model=PortfolioResponse,
)
async def get_portfolio(
    portfolio_id: int,
    current_user: User = Depends(get_current_user),
    service: PortfolioService = Depends(get_portfolio_service),
):
    return await service.get_portfolio(
        portfolio_id,
        current_user.id,
    )


@router.put(
    "/{portfolio_id}",
    response_model=PortfolioResponse,
)
async def update_portfolio(
    portfolio_id: int,
    request: PortfolioUpdate,
    current_user: User = Depends(get_current_user),
    service: PortfolioService = Depends(get_portfolio_service),
):
    return await service.update_portfolio(
        portfolio_id,
        current_user.id,
        request,
    )


@router.delete("/{portfolio_id}")
async def delete_portfolio(
    portfolio_id: int,
    current_user: User = Depends(get_current_user),
    service: PortfolioService = Depends(get_portfolio_service),
):
    return await service.delete_portfolio(
        portfolio_id,
        current_user.id,
    )