import asyncio
from datetime import datetime, timezone
from time import monotonic

import yfinance as yf

from app.schemas.market import MarketDataResponse


class MarketDataService:
    _quote_cache: dict[str, tuple[float, dict]] = {}
    _cache_ttl_seconds = 45

    async def _get_info(self, ticker: str) -> dict:
        """Fetch quotes off the event loop and reuse very recent results."""
        cached = self._quote_cache.get(ticker)
        if cached and monotonic() - cached[0] < self._cache_ttl_seconds:
            return cached[1]

        info = await asyncio.to_thread(
            lambda: yf.Ticker(ticker).info or {},
        )
        self._quote_cache[ticker] = (monotonic(), info)
        return info

    async def get_market_data(
        self,
        ticker: str,
    ) -> MarketDataResponse | None:

        ticker = self._normalize_ticker(ticker)

        info = await self._get_info(ticker)

        if not info:
            return None

        current_price = info.get("currentPrice")
        if current_price is None:
            current_price = info.get("regularMarketPrice")

        return MarketDataResponse(
            ticker=ticker,
            company_name=info.get(
                "longName",
                ticker,
            ),
            current_price=current_price,
            previous_close=info.get(
                "previousClose"
            ),
            open_price=info.get(
                "open"
            ),
            day_high=info.get(
                "dayHigh"
            ),
            day_low=info.get(
                "dayLow"
            ),
            fifty_two_week_high=info.get(
                "fiftyTwoWeekHigh"
            ),
            fifty_two_week_low=info.get(
                "fiftyTwoWeekLow"
            ),
            volume=info.get(
                "volume"
            ),
            market_cap=info.get(
                "marketCap"
            ),
            pe_ratio=info.get(
                "trailingPE"
            ),
            dividend_yield=info.get(
                "dividendYield"
            ),
            currency=info.get(
                "currency"
            ),
            exchange=info.get(
                "exchange"
            ),
            price_as_of=self._quote_time(info.get("regularMarketTime")),
            fetched_at=datetime.now(timezone.utc),
        )

    async def get_current_price(
        self,
        ticker: str,
    ) -> float | None:

        ticker = self._normalize_ticker(ticker)

        info = await self._get_info(ticker)

        price = info.get("currentPrice")

        if price is None:
            price = info.get(
                "regularMarketPrice"
            )

        return price

    async def get_current_quote(
        self,
        ticker: str,
    ) -> tuple[float | None, datetime | None]:
        """Return the latest price together with its provider timestamp."""
        ticker = self._normalize_ticker(ticker)
        info = await self._get_info(ticker)

        price = info.get("currentPrice")
        if price is None:
            price = info.get("regularMarketPrice")

        return price, self._quote_time(info.get("regularMarketTime"))

    async def get_stock_metadata(
        self,
        ticker: str,
    ) -> dict | None:

        ticker = self._normalize_ticker(ticker)

        info = await self._get_info(ticker)

        if not info:
            return None

        return {
            "ticker": ticker,
            "company_name": info.get(
                "longName",
                ticker,
            ),
            "exchange": info.get(
                "exchange"
            ),
            "sector": info.get(
                "sector"
            ),
            "industry": info.get(
                "industry"
            ),
            "currency": info.get(
                "currency"
            ),
            "country": info.get(
                "country"
            ),
            "asset_type": "STOCK",
        }

    @staticmethod
    def _normalize_ticker(
        ticker: str,
    ) -> str:

        ticker = ticker.strip().upper()

        # Automatically use NSE
        # for Indian stocks.
        if "." not in ticker:
            ticker = f"{ticker}.NS"

        return ticker

    @staticmethod
    def _quote_time(value: object) -> datetime | None:
        if isinstance(value, datetime):
            return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
        if isinstance(value, (int, float)):
            return datetime.fromtimestamp(value, tz=timezone.utc)
        return None
