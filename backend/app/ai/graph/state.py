from typing import Any, TypedDict


class FinGenieState(TypedDict, total=False):

    # User information
    message: str
    user_id: int
    portfolio_id: int | None

    # Conversation
    conversation_history: list[dict]

    # Agent decision
    tool_name: str
    tool_arguments: dict

    # Tool execution
    tool_result: Any
    tool_error: str | None

    # Final response
    response: str

    # RAG sources
    sources: list[dict]