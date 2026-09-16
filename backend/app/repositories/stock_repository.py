from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.stock import Stock


class StockRepository:

    def __init__(
        self,
        db: AsyncSession,
    ):
        self.db = db

    async def get_by_ticker(
        self,
        ticker: str,
    ) -> Stock | None:

        result = await self.db.execute(
            select(Stock).where(
                Stock.ticker == ticker
            )
        )

        return result.scalar_one_or_none()

    async def search(
        self,
        query: str,
    ) -> list[Stock]:

        result = await self.db.execute(
            select(Stock).where(
                or_(
                    Stock.ticker.ilike(
                        f"%{query}%"
                    ),
                    Stock.company_name.ilike(
                        f"%{query}%"
                    ),
                )
            )
        )

        return result.scalars().all()

    async def create(
        self,
        stock: Stock,
    ) -> Stock:

        self.db.add(stock)

        await self.db.commit()

        await self.db.refresh(stock)

        return stock

    async def rollback(self):
        await self.db.rollback()