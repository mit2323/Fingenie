from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from app.models.holding import Holding



class HoldingRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        holding: Holding,
    ):
        self.db.add(holding)

        await self.db.commit()

        await self.db.refresh(holding)

        return holding

    async def get_by_id(
        self,
        holding_id: int,
    ):
        result = await self.db.execute(
            select(Holding).where(
                Holding.id == holding_id
            )
        )

        return result.scalar_one_or_none()

    async def get_by_portfolio(
    self,
    portfolio_id: int,
    ):
        result = await self.db.execute(
        select(Holding)
        .options(
            joinedload(Holding.stock)
        )
        .where(
            Holding.portfolio_id == portfolio_id
        )
        )

        return result.scalars().all()

    async def get_by_portfolio_and_stock(
    self,
    portfolio_id: int,
    stock_id: int,
    ):
     result = await self.db.execute(
        select(Holding)
        .options(joinedload(Holding.stock))
        .where(
            Holding.portfolio_id == portfolio_id,
            Holding.stock_id == stock_id,
        )
    )

     return result.scalar_one_or_none()

    async def update(self):
        await self.db.commit()

    async def delete(
        self,
        holding: Holding,
    ):
        await self.db.delete(holding)
        await self.db.commit()
