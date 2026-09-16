from fastapi import HTTPException, status

from app.repositories.conversation_repository import (
    ConversationRepository,
)
from app.schemas.conversation import ConversationCreate


class ConversationService:

    def __init__(
        self,
        repository: ConversationRepository,
    ):
        self.repository = repository

    async def create(
        self,
        request: ConversationCreate,
        user_id: int,
    ):

        return await self.repository.create_conversation(
            user_id=user_id,
            title=request.title,
        )

    async def get_all(
        self,
        user_id: int,
    ):

        return await self.repository.get_user_conversations(
            user_id=user_id,
        )

    async def get_by_id(
        self,
        conversation_id: int,
        user_id: int,
    ):

        conversation = (
            await self.repository.get_by_id(
                conversation_id=conversation_id,
                user_id=user_id,
            )
        )

        if conversation is None:

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found.",
            )

        return conversation

    async def delete(
        self,
        conversation_id: int,
        user_id: int,
    ):

        conversation = (
            await self.repository.get_by_id(
                conversation_id=conversation_id,
                user_id=user_id,
            )
        )

        if conversation is None:

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found.",
            )

        await self.repository.delete(
            conversation
        )