from datetime import datetime, timezone

from fastapi import HTTPException, status

from app.models.holding import Holding
from app.repositories.holding_repository import HoldingRepository
from app.repositories.portfolio_repository import PortfolioRepository
from app.schemas.holding import HoldingCreate, HoldingUpdate
from app.schemas.holding import HoldingResponse
from app.services.market_data_service import MarketDataService
from app.services.stock_service import StockService


class HoldingService:
    def __init__(
        self,
        holding_repository: HoldingRepository,
        portfolio_repository: PortfolioRepository,
        stock_service: StockService,
    ):
        self.holding_repository = holding_repository
        self.portfolio_repository = portfolio_repository
        self.stock_service = stock_service
        self.market_service = MarketDataService()

    async def create_holding(
        self,
        user_id: int,
        request: HoldingCreate,
    ):
        portfolio = await self.portfolio_repository.get_by_id_and_user(
            request.portfolio_id,
            user_id,
        )

        if portfolio is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Portfolio not found.",
            )

        stock = await self.stock_service.get_or_create_stock(
            request.ticker,
        )

        if stock is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invalid stock ticker.",
            )

        existing = await self.holding_repository.get_by_portfolio_and_stock(
            request.portfolio_id,
            stock.id,
        )

        if existing:
            total_quantity = (
                existing.quantity
                + request.quantity
            )

            total_cost = (
                existing.quantity * existing.average_buy_price
            ) + (
                request.quantity * request.buy_price
            )

            existing.quantity = total_quantity
            existing.average_buy_price = (
                total_cost / total_quantity
            )

            await self.holding_repository.save_changes()

            return existing

        holding = Holding(
            portfolio_id=request.portfolio_id,
            stock_id=stock.id,
            quantity=request.quantity,
            average_buy_price=request.buy_price,
        )

        return await self.holding_repository.create(
            holding
        )

    async def get_holdings(
        self,
        portfolio_id: int,
        user_id: int,
    ):
        portfolio = await self.portfolio_repository.get_by_id_and_user(
            portfolio_id,
            user_id,
        )

        if portfolio is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Portfolio not found.",
            )

        holdings = await self.holding_repository.get_by_portfolio(portfolio_id)
        return [await self._with_live_quote(holding) for holding in holdings]

    async def _with_live_quote(self, holding: Holding) -> HoldingResponse:
        """Build a holding response with a newly fetched market valuation."""
        try:
            current_price, price_as_of = await self.market_service.get_current_quote(
                holding.stock.ticker,
            )
        except Exception:
            # A temporary provider failure should not make saved holdings
            # disappear from the portfolio screen.
            current_price, price_as_of = None, None
        investment = holding.quantity * holding.average_buy_price
        current_value = holding.quantity * current_price if current_price is not None else None
        profit_loss = current_value - investment if current_value is not None else None
        profit_loss_percentage = (
            (profit_loss / investment) * 100
            if profit_loss is not None and investment
            else None
        )

        return HoldingResponse(
            id=holding.id,
            portfolio_id=holding.portfolio_id,
            stock_id=holding.stock_id,
            quantity=holding.quantity,
            average_buy_price=holding.average_buy_price,
            created_at=holding.created_at,
            ticker=holding.stock.ticker,
            company_name=holding.stock.company_name,
            current_price=round(current_price, 2) if current_price is not None else None,
            price_as_of=price_as_of,
            price_fetched_at=datetime.now(timezone.utc),
            current_value=round(current_value, 2) if current_value is not None else None,
            profit_loss=round(profit_loss, 2) if profit_loss is not None else None,
            profit_loss_percentage=(
                round(profit_loss_percentage, 2)
                if profit_loss_percentage is not None
                else None
            ),
        )

    async def get_holding(
        self,
        holding_id: int,
        user_id: int,
    ):
        holding = await self.holding_repository.get_by_id(
            holding_id
        )

        if holding is None or await self.portfolio_repository.get_by_id_and_user(
            holding.portfolio_id,
            user_id,
        ) is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Holding not found.",
            )

        return holding

    async def update_holding(
        self,
        holding_id: int,
        user_id: int,
        request: HoldingUpdate,
    ):
        holding = await self.get_holding(holding_id, user_id)

        if request.quantity is not None:
            holding.quantity = request.quantity

        if request.buy_price is not None:
            holding.average_buy_price = request.buy_price

        await self.holding_repository.save_changes()

        return holding

    async def delete_holding(
        self,
        holding_id: int,
        user_id: int,
    ):
        holding = await self.get_holding(holding_id, user_id)

        await self.holding_repository.delete(
            holding
        )

        return {
            "message": "Holding deleted successfully."
        }
