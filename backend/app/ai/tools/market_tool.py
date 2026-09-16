from app.services.market_data_service import MarketDataService


class MarketTool:

    def __init__(
        self,
        market_service: MarketDataService,
    ):
        self.market_service = market_service

    async def execute(
        self,
        ticker: str,
    ) -> dict | None:

        market_data = await self.market_service.get_market_data(
            ticker=ticker,
        )

        if market_data is None:
            return None

        return {
            "ticker": market_data.ticker,
            "company_name": market_data.company_name,
            "current_price": market_data.current_price,
            "previous_close": market_data.previous_close,
            "open_price": market_data.open_price,
            "day_high": market_data.day_high,
            "day_low": market_data.day_low,
            "fifty_two_week_high": market_data.fifty_two_week_high,
            "fifty_two_week_low": market_data.fifty_two_week_low,
            "volume": market_data.volume,
            "market_cap": market_data.market_cap,
            "pe_ratio": market_data.pe_ratio,
            "dividend_yield": market_data.dividend_yield,
            "currency": market_data.currency,
            "exchange": market_data.exchange,
        }