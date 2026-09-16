from datetime import datetime

from pydantic import BaseModel, ConfigDict


class StockResponse(BaseModel):
    id: int
    ticker: str
    company_name: str
    exchange: str
    sector: str | None = None
    industry: str | None = None
    currency: str
    country: str
    asset_type: str

    model_config = ConfigDict(
        from_attributes=True,
    )


class StockSearchResponse(BaseModel):
    ticker: str
    company_name: str
    exchange: str