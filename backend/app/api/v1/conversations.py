from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.repositories.conversation_repository import (
    ConversationRepository,
)
from app.schemas.conversation import (
    ConversationCreate,
    ConversationDetailResponse,
    ConversationResponse,
)
from app.services.conversation_service import (
    ConversationService,
)


router = APIRouter(
    prefix="/conversations",
    tags=["Conversations"],
)


def get_conversation_service(
    db: AsyncSession = Depends(get_db),
) -> ConversationService:

    repository = ConversationRepository(db)

    return ConversationService(
        repository=repository,
    )


@router.post(
    "",
    response_model=ConversationResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_conversation(
    request: ConversationCreate,
    current_user: User = Depends(get_current_user),
    service: ConversationService = Depends(
        get_conversation_service
    ),
):

    return await service.create(
        request=request,
        user_id=current_user.id,
    )


@router.get(
    "",
    response_model=list[ConversationResponse],
)
async def get_conversations(
    current_user: User = Depends(get_current_user),
    service: ConversationService = Depends(
        get_conversation_service
    ),
):

    return await service.get_all(
        user_id=current_user.id,
    )


@router.get(
    "/{conversation_id}",
    response_model=ConversationDetailResponse,
)
async def get_conversation(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    service: ConversationService = Depends(
        get_conversation_service
    ),
):

    return await service.get_by_id(
        conversation_id=conversation_id,
        user_id=current_user.id,
    )


@router.delete(
    "/{conversation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_conversation(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    service: ConversationService = Depends(
        get_conversation_service
    ),
):

    await service.delete(
        conversation_id=conversation_id,
        user_id=current_user.id,
    )

    return None