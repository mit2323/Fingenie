from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.constants import API_V1_PREFIX
from app.core.logger import logger
from app.services.ai_runtime import get_ai_runtime
from app.exceptions.handlers import register_exception_handlers
from app.utils.response import success_response
from fastapi import FastAPI

from app.core.exception_handlers import (
    value_error_handler,
    general_exception_handler,
)
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting FinGenie...")
    # Create the lightweight provider client once. The substantially heavier
    # RAG embedding model remains lazy until document search is requested.
    app.state.ai_runtime = get_ai_runtime()
    yield
    logger.info("Shutting down FinGenie...")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    lifespan=lifespan,
)
app.add_exception_handler(
    ValueError,
    value_error_handler,
)

app.add_exception_handler(
    Exception,
    general_exception_handler,
)
register_exception_handlers(app)
@app.get("/", tags=["Root"])
async def root():
    return success_response(
        message="Welcome to FinGenie API",
        data={
            "name": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "docs": "/docs",
            "redoc": "/redoc",
            "health": "/api/v1/health",
        },
    )
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    api_router,
    prefix=API_V1_PREFIX,
)
