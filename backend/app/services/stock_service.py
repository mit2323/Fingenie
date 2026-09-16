from sqlalchemy.exc import IntegrityError

from app.models.stock import Stock
from app.repositories.stock_repository import StockRepository
from app.services.market_data_service import MarketDataService


class StockService:

    def __init__(
        self,
        repository: StockRepository,
    ):
        self.repository = repository
        self.market_service = MarketDataService()

    async def get_or_create_stock(
        self,
        ticker: str,
    ):

        ticker = ticker.strip().upper()

        # Normalize ticker for Indian stocks
        if "." not in ticker:
            ticker = f"{ticker}.NS"

        # 1. Check existing stock

        stock = await self.repository.get_by_ticker(
            ticker
        )

        if stock:
            return stock

        # 2. Fetch metadata
        metadata = (
            await self.market_service.get_stock_metadata(
                ticker
            )
        )

        if metadata is None:
            return None

        # 3. Prepare stock

        stock = Stock(
            ticker=metadata["ticker"],
            company_name=metadata["company_name"],
            exchange=metadata["exchange"],
            sector=metadata["sector"],
            industry=metadata["industry"],
            currency=metadata["currency"],
            country=metadata["country"],
            asset_type=metadata["asset_type"],
        )

        # 4. Try to create
        try:

            return await self.repository.create(
                stock
            )

        except IntegrityError:

            # Another request may have created
            # the same ticker at the same time.

            await self.repository.rollback()

            # Fetch the stock that now exists
            existing_stock = (
                await self.repository.get_by_ticker(
                    ticker
                )
            )

            if existing_stock:
                return existing_stock

            raise

    async def search_stock(
        self,
        query: str,
    ):
        return await self.repository.search(
            query
        )