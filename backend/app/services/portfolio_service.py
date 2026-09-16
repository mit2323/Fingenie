from fastapi import HTTPException, status

from app.models.portfolio import Portfolio
from app.repositories.portfolio_repository import PortfolioRepository
from app.schemas.portfolio import (
    PortfolioCreate,
    PortfolioUpdate,
)


class PortfolioService:
    def __init__(self, repository: PortfolioRepository):
        self.repository = repository

    async def create_portfolio(
        self,
        user_id: int,
        request: PortfolioCreate,
    ):
        existing = await self.repository.get_by_name(
            request.name,
            user_id,
        )

        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Portfolio with this name already exists.",
            )

        portfolio = Portfolio(
            user_id=user_id,
            name=request.name,
            base_currency=request.base_currency,
        )

        return await self.repository.create(portfolio)

    async def get_all_portfolios(
        self,
        user_id: int,
    ):
        return await self.repository.get_all_by_user(user_id)

    async def get_portfolio(
        self,
        portfolio_id: int,
        user_id: int,
    ):
        portfolio = await self.repository.get_by_id_and_user(
            portfolio_id,
            user_id,
        )

        if portfolio is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Portfolio not found.",
            )

        return portfolio

    async def update_portfolio(
        self,
        portfolio_id: int,
        user_id: int,
        request: PortfolioUpdate,
    ):
        portfolio = await self.get_portfolio(
            portfolio_id,
            user_id,
        )

        if request.name is not None:
            portfolio.name = request.name

        if request.base_currency is not None:
            portfolio.base_currency = request.base_currency

        await self.repository.update()

        return portfolio

    async def delete_portfolio(
        self,
        portfolio_id: int,
        user_id: int,
    ):
        portfolio = await self.get_portfolio(
            portfolio_id,
            user_id,
        )

        await self.repository.delete(portfolio)

        return {
            "message": "Portfolio deleted successfully."
        }