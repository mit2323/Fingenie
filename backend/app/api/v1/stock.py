from fastapi import APIRouter, Depends

from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.repositories.stock_repository import StockRepository
from app.schemas.stock import (
    StockResponse,
)
from app.services.stock_service import StockService

router = APIRouter(
    prefix="/stocks",
    tags=["Stocks"],
)


def get_stock_service(
    db: AsyncSession = Depends(get_db),
):
    repository = StockRepository(db)
    return StockService(repository)


@router.get(
    "/{ticker}",
    response_model=StockResponse,
)
async def get_stock(
    ticker: str,
    service: StockService = Depends(get_stock_service),
):
    return await service.get_or_create_stock(
        ticker
    )