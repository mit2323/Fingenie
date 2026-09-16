from pydantic import BaseModel, Field


class ChatRequest(BaseModel):

    message: str = Field(
        min_length=1,
        max_length=2000,
    )

    portfolio_id: int | None = None

    conversation_id: int | None = None


class ChatSource(BaseModel):

    source: str

    chunk_index: int


class ChatResponse(BaseModel):

    message: str

    intent: str

    conversation_id: int

    sources: list[ChatSource] = Field(
        default_factory=list
    )