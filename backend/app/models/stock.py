from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.base import Base


class Stock(Base):
    __tablename__ = "stocks"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    ticker = Column(
        String(20),
        unique=True,
        nullable=False,
        index=True,
    )

    company_name = Column(
        String(255),
        nullable=False,
    )

    exchange = Column(
        String(20),
        nullable=False,
    )

    sector = Column(
        String(100),
        nullable=True,
    )

    industry = Column(
        String(150),
        nullable=True,
    )

    isin = Column(
        String(20),
        unique=True,
        nullable=True,
    )

    currency = Column(
        String(10),
        nullable=False,
        default="INR",
    )

    country = Column(
        String(100),
        nullable=False,
        default="India",
    )

    asset_type = Column(
        String(50),
        nullable=False,
        default="Equity",
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    holdings = relationship(
        "Holding",
        back_populates="stock",
    )