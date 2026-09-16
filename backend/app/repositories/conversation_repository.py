from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.chat_message import ChatMessage
from app.models.conversation import Conversation


class ConversationRepository:

    def __init__(
        self,
        db: AsyncSession,
    ):
        self.db = db

    async def create_conversation(
        self,
        user_id: int,
        title: str | None = None,
    ) -> Conversation:

        conversation = Conversation(
            user_id=user_id,
            title=title,
        )

        self.db.add(conversation)

        await self.db.commit()

        await self.db.refresh(conversation)

        return conversation

    async def get_by_id(
        self,
        conversation_id: int,
        user_id: int,
    ) -> Conversation | None:

        result = await self.db.execute(
            select(Conversation).where(
                Conversation.id == conversation_id,
                Conversation.user_id == user_id,
            )
        )

        return result.scalar_one_or_none()

    async def add_message(
        self,
        conversation_id: int,
        role: str,
        content: str,
    ) -> ChatMessage:

        message = ChatMessage(
            conversation_id=conversation_id,
            role=role,
            content=content,
        )

        self.db.add(message)

        await self.db.commit()

        await self.db.refresh(message)

        return message

    async def get_recent_messages(
        self,
        conversation_id: int,
        limit: int = 10,
    ) -> list[ChatMessage]:

        result = await self.db.execute(
            select(ChatMessage)
            .where(
                ChatMessage.conversation_id
                == conversation_id
            )
            .order_by(
                ChatMessage.created_at.desc()
            )
            .limit(limit)
        )

        messages = result.scalars().all()

        return list(reversed(messages))
    async def get_user_conversations(
    self,
    user_id: int,
    ) -> list[Conversation]:

        result = await self.db.execute(
        select(Conversation)
        .where(
            Conversation.user_id == user_id
        )
        .order_by(
            Conversation.updated_at.desc()
        )
    )

        return list(result.scalars().all())


    async def delete(
    self,
    conversation: Conversation,
    ) -> None:

        await self.db.delete(conversation)

        await self.db.commit()