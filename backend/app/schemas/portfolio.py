from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class PortfolioCreate(BaseModel):
    name: str = Field(
        ...,
        min_length=3,
        max_length=100,
    )

    base_currency: str = Field(
        default="INR",
        max_length=10,
    )


class PortfolioUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=3,
        max_length=100,
    )

    base_currency: str | None = Field(
        default=None,
        max_length=10,
    )


class PortfolioResponse(BaseModel):
    id: int
    name: str
    base_currency: str
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )