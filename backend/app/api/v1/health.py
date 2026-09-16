from fastapi import APIRouter
from app.core.config import settings
router = APIRouter(tags=["Health"])
from app.utils.response import success_response
from app.core.config import settings

@router.get("/health")
async def health():

    return success_response(
        message="API is healthy",
        data={
            "service": settings.APP_NAME,
            "version": settings.APP_VERSION,
        },
    )