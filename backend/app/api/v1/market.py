from fastapi import APIRouter, HTTPException

from app.schemas.market import MarketDataResponse
from app.services.market_data_service import MarketDataService

router = APIRouter(
    prefix="/market",
    tags=["Market"],
)

market_service = MarketDataService()


@router.get(
    "/{ticker}",
    response_model=MarketDataResponse,
)
async def get_market_data(
    ticker: str,
):

    data = await market_service.get_market_data(
        ticker,
    )

    if data is None:
        raise HTTPException(
            status_code=404,
            detail="Stock not found.",
        )

    return data