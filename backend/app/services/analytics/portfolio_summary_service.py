from fastapi import HTTPException, status

from app.repositories.holding_repository import HoldingRepository
from app.repositories.portfolio_repository import PortfolioRepository
from app.schemas.portfolio_summary import PortfolioSummaryResponse
from app.services.market_data_service import MarketDataService


class PortfolioSummaryService:

    def __init__(
        self,
        holding_repository: HoldingRepository,
        portfolio_repository: PortfolioRepository,
    ):
        self.holding_repository = holding_repository
        self.portfolio_repository = portfolio_repository
        self.market_service = MarketDataService()

    async def get_summary(
        self,
        portfolio_id: int,
        user_id: int,
    ) -> PortfolioSummaryResponse:

        # Verify portfolio ownership
        portfolio = await self.portfolio_repository.get_by_id_and_user(
            portfolio_id,
            user_id,
        )

        if portfolio is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Portfolio not found.",
            )

        # Fetch all holdings
        holdings = await self.holding_repository.get_by_portfolio(
            portfolio_id,
        )

        total_investment = 0.0
        current_value = 0.0

        # Calculate portfolio values
        for holding in holdings:

            investment = (
                holding.quantity *
                holding.average_buy_price
            )

            total_investment += investment

            current_price = await self.market_service.get_current_price(
                holding.stock.ticker
            )

            # Skip if current price is unavailable
            if current_price is None:
                current_value += investment
                continue

            current_value += (
                holding.quantity *
                current_price
            )

        profit_loss = current_value - total_investment

        if total_investment > 0:
            return_percentage = (
                profit_loss / total_investment
            ) * 100
        else:
            return_percentage = 0.0

        return PortfolioSummaryResponse(
            total_investment=round(total_investment, 2),
            current_value=round(current_value, 2),
            profit_loss=round(profit_loss, 2),
            return_percentage=round(return_percentage, 2),
            holding_count=len(holdings),
        )