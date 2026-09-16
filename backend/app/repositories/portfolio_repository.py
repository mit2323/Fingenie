from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.portfolio import Portfolio


class PortfolioRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, portfolio: Portfolio):
        self.db.add(portfolio)
        await self.db.commit()
        await self.db.refresh(portfolio)
        return portfolio

    async def get_by_id(
        self,
        portfolio_id: int,
    ):
        result = await self.db.execute(
            select(Portfolio).where(
                Portfolio.id == portfolio_id
            )
        )
        return result.scalar_one_or_none()

    async def get_by_id_and_user(
        self,
        portfolio_id: int,
        user_id: int,
    ):
        result = await self.db.execute(
            select(Portfolio).where(
                Portfolio.id == portfolio_id,
                Portfolio.user_id == user_id,
            )
        )
        return result.scalar_one_or_none()

    async def get_all_by_user(
        self,
        user_id: int,
    ):
        result = await self.db.execute(
            select(Portfolio).where(
                Portfolio.user_id == user_id
            )
        )
        return result.scalars().all()

    async def get_by_name(
        self,
        name: str,
        user_id: int,
    ):
        result = await self.db.execute(
            select(Portfolio).where(
                Portfolio.name == name,
                Portfolio.user_id == user_id,
            )
        )
        return result.scalar_one_or_none()

    async def update(self):
        await self.db.commit()

    async def delete(
        self,
        portfolio: Portfolio,
    ):
        await self.db.delete(portfolio)
        await self.db.commit()