from pydantic import BaseModel


class PortfolioSummaryResponse(BaseModel):

    total_investment: float

    current_value: float

    profit_loss: float

    return_percentage: float

    holding_count: int