from fastapi import APIRouter
from app.api.v1.auth import router as auth_router
from app.api.v1.health import router as health_router
from app.api.v1.portfolio import router as portfolio_router
from app.api.v1.stock import router as stock_router
from app.api.v1.holding import router as holding_router
from app.api.v1.portfolio_summary import (
    router as portfolio_summary_router,
)
from app.api.v1.analytics import router as analytics_router
from app.api.v1.market import router as market_router
from app.api.v1.chat import router as chat_router
from app.api.v1.conversations import (
    router as conversations_router,
)
from app.api.v1 import knowledge
api_router = APIRouter()
api_router.include_router(holding_router)
api_router.include_router(stock_router)
api_router.include_router(portfolio_router)
api_router.include_router(health_router)
api_router.include_router(auth_router)
api_router.include_router(
    portfolio_summary_router
)
api_router.include_router(
    analytics_router
)

api_router.include_router(
    market_router
)
api_router.include_router(
    chat_router
)
api_router.include_router(
    knowledge.router
)
api_router.include_router(
    conversations_router
)