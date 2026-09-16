from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class HoldingCreate(BaseModel):
    portfolio_id: int
    ticker: str = Field(
        ...,
        min_length=1,
        max_length=20,
    )
    quantity: float = Field(
        ...,
        gt=0,
    )
    buy_price: float = Field(
        ...,
        gt=0,
    )


class HoldingUpdate(BaseModel):
    quantity: float = Field(
        ...,
        gt=0,
    )
    buy_price: float = Field(
        ...,
        gt=0,
    )


class HoldingResponse(BaseModel):
    id: int
    portfolio_id: int
    stock_id: int
    quantity: float
    average_buy_price: float
    created_at: datetime
    ticker: str | None = None
    company_name: str | None = None
    current_price: float | None = None
    price_as_of: datetime | None = None
    price_fetched_at: datetime | None = None
    current_value: float | None = None
    profit_loss: float | None = None
    profit_loss_percentage: float | None = None

    model_config = ConfigDict(
        from_attributes=True,
    )
