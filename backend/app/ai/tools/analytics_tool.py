from app.services.analytics.allocation_service import AllocationService


class AnalyticsTool:

    def __init__(
        self,
        allocation_service: AllocationService,
    ):
        self.allocation_service = allocation_service

    async def execute(
        self,
        portfolio_id: int,
        user_id: int,
    ) -> list[dict]:

        allocations = await self.allocation_service.get_sector_allocation(
            portfolio_id=portfolio_id,
            user_id=user_id,
        )

        return [
            {
                "sector": allocation.sector,
                "investment": allocation.investment,
                "percentage": allocation.percentage,
            }
            for allocation in allocations
        ]