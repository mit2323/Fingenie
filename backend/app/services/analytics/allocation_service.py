from fastapi import HTTPException, status

from app.repositories.holding_repository import HoldingRepository
from app.repositories.portfolio_repository import PortfolioRepository
from app.schemas.allocation import SectorAllocationResponse


class AllocationService:

    def __init__(
        self,
        holding_repository: HoldingRepository,
        portfolio_repository: PortfolioRepository,
    ):
        self.holding_repository = holding_repository
        self.portfolio_repository = portfolio_repository

    async def get_sector_allocation(
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

        holdings = await self.holding_repository.get_by_portfolio(
            portfolio_id,
        )

        total_investment = 0.0
        sector_map = {}

        for holding in holdings:

            investment = (
                holding.quantity *
                holding.average_buy_price
            )

            total_investment += investment

            sector = (
                holding.stock.sector
                or "Unknown"
            )

            sector_map[sector] = (
                sector_map.get(sector, 0)
                + investment
            )

        response = []

        for sector, investment in sector_map.items():

            percentage = 0.0

            if total_investment > 0:
                percentage = (
                    investment /
                    total_investment
                ) * 100

            response.append(
                SectorAllocationResponse(
                    sector=sector,
                    investment=round(investment, 2),
                    percentage=round(percentage, 2),
                )
            )

        response.sort(
            key=lambda x: x.investment,
            reverse=True,
        )

        return response