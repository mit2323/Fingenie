from datetime import datetime

from pydantic import BaseModel


class MarketDataResponse(BaseModel):
    ticker: str
    company_name: str

    current_price: float | None

    previous_close: float | None

    open_price: float | None

    day_high: float | None

    day_low: float | None

    fifty_two_week_high: float | None

    fifty_two_week_low: float | None

    volume: int | None

    market_cap: int | None

    pe_ratio: float | None

    dividend_yield: float | None

    currency: str | None

    exchange: str | None

    # `price_as_of` is supplied by the market-data provider when available.
    # `fetched_at` is always present so clients can distinguish a fresh
    # retrieval from the time at which the exchange published the quote.
    price_as_of: datetime | None
    fetched_at: datetime
