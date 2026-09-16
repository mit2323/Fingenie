from app.services.analytics.portfolio_summary_service import PortfolioSummaryService
from app.services.analytics.portfolio_summary_service import (
    PortfolioSummaryService,
)

class PortfolioTool:

    def __init__(
        self,
        summary_service: PortfolioSummaryService,
    ):
        self.summary_service = summary_service

    async def execute(
        self,
        portfolio_id: int,
        user_id: int,
        ) -> dict:

            summary = await self.summary_service.get_summary(
            portfolio_id=portfolio_id,
            user_id=user_id,
            )

            return {
            "total_investment": summary.total_investment,
            "current_value": summary.current_value,
            "profit_loss": summary.profit_loss,
            "return_percentage": summary.return_percentage,
            "holding_count": summary.holding_count,
        }