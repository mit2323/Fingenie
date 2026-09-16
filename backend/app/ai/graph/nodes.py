import json
import re

from app.ai.graph.state import FinGenieState
from app.services.gemini_service import GeminiService


# ============================================================
# RAG QUERY REWRITER
# ============================================================


def fast_route(
    message: str,
    portfolio_id: int | None,
) -> tuple[str, dict] | None:
    """Avoid a classifier call for unambiguous, common financial requests."""
    normalized = message.lower()

    if portfolio_id is not None:
        if "sector" in normalized and any(
            term in normalized
            for term in ("allocation", "exposure", "diversification", "concentration")
        ):
            return "get_sector_allocation", {"portfolio_id": portfolio_id}

        if "portfolio" in normalized and any(
            term in normalized
            for term in ("summary", "performance", "value", "return", "profit", "loss", "investment")
        ):
            return "get_portfolio_summary", {"portfolio_id": portfolio_id}

    if any(term in normalized for term in ("stock price", "current price", "share price", "quote")):
        ticker_match = re.search(
            r"(?:of|for)\s+([A-Za-z]{1,12})(?:\.[A-Za-z]{1,4})?\b",
            message,
            flags=re.IGNORECASE,
        )
        if ticker_match:
            return "get_market_data", {"ticker": ticker_match.group(1).upper()}

    ticker_first_match = re.search(
        r"\b([A-Z]{1,12})\b\s+(?:stock\s+)?(?:price|quote)\b",
        message,
    )
    if ticker_first_match:
        return "get_market_data", {"ticker": ticker_first_match.group(1)}

    return None

async def rewrite_rag_query(
    message: str,
    conversation_history: list[dict],
    gemini_service: GeminiService,
) -> str:

    # If there is no conversation history,
    # the question is already standalone.
    if not conversation_history:
        return message

    history_text = "\n".join(
        f"{item.get('role', 'user')}: "
        f"{item.get('content', '')}"
        for item in conversation_history
    )

    prompt = f"""
You are helping FinGenie understand a user's
follow-up question.

Conversation history:

{history_text}

Current question:

{message}

Rewrite the current question into a standalone
question that can be searched in a financial
knowledge base.

Rules:

1. Preserve the user's original meaning.

2. Resolve references such as:
   - it
   - this
   - that
   - they
   - them
   - the above

   using the conversation history.

3. Do not answer the question.

4. Do not add information that is not present
   in the conversation.

5. If the question is already standalone,
   return it unchanged.

Return ONLY the rewritten question.
"""

    rewritten = await gemini_service.generate_response(
        prompt
    )

    rewritten = rewritten.strip()

    # Safety fallback
    if not rewritten:
        return message

    return rewritten


# ============================================================
# AGENT NODE
# ============================================================

async def agent_node(
    state: FinGenieState,
    gemini_service: GeminiService,
) -> FinGenieState:

    message = state["message"]

    portfolio_id = state.get(
        "portfolio_id"
    )

    conversation_history = state.get(
        "conversation_history",
        [],
    )

    direct_route = fast_route(message, portfolio_id)
    if direct_route is not None:
        tool_name, arguments = direct_route
        return {
            **state,
            "tool_name": tool_name,
            "tool_arguments": arguments,
        }

    # --------------------------------
    # Format conversation history
    # --------------------------------

    if conversation_history:

        history_text = "\n".join(
            f"{item.get('role', 'user')}: "
            f"{item.get('content', '')}"
            for item in conversation_history
        )

    else:

        history_text = (
            "No previous conversation."
        )

    # --------------------------------
    # Tool selection prompt
    # --------------------------------

    prompt = f"""
You are the tool-selection component of FinGenie,
an AI financial copilot.

Determine which backend tool should handle
the user's question.

Available tools:

1. get_portfolio_summary

Use for:

- portfolio performance
- total investment
- portfolio value
- profit/loss
- portfolio returns
- holdings summary

2. get_sector_allocation

Use for:

- sector allocation
- diversification
- sector exposure
- portfolio concentration

3. get_market_data

Use for:

- current stock price
- 52-week high
- 52-week low
- market capitalization
- trading volume
- PE ratio
- dividend yield
- current stock information

4. search_financial_knowledge

Use for:

- financial concepts
- investment principles
- investor education
- financial regulations
- uploaded financial documents
- questions requiring the financial knowledge base

5. general

Use when no backend financial tool is required.

Use conversation history for follow-up questions.

Return ONLY valid JSON.

Examples:

{{
    "tool": "get_portfolio_summary",
    "arguments": {{
        "portfolio_id": 1
    }}
}}

{{
    "tool": "get_sector_allocation",
    "arguments": {{
        "portfolio_id": 1
    }}
}}

{{
    "tool": "get_market_data",
    "arguments": {{
        "ticker": "TCS"
    }}
}}

{{
    "tool": "search_financial_knowledge",
    "arguments": {{
        "query": "What is diversification?"
    }}
}}

{{
    "tool": "general",
    "arguments": {{}}
}}

Authenticated portfolio ID:

{portfolio_id}

Conversation history:

{history_text}

Current question:

{message}
"""

    # --------------------------------
    # Ask Gemini
    # --------------------------------

    response = (
        await gemini_service.generate_response(
            prompt
        )
    )

    # --------------------------------
    # Parse JSON
    # --------------------------------

    response = response.strip()

    if response.startswith("```"):

        response = (
            response
            .replace("```json", "")
            .replace("```", "")
            .strip()
        )

    try:

        selection = json.loads(
            response
        )

    except json.JSONDecodeError:

        selection = {
            "tool": "general",
            "arguments": {},
        }

    # --------------------------------
    # Validate tool
    # --------------------------------

    allowed_tools = {
        "get_portfolio_summary",
        "get_sector_allocation",
        "get_market_data",
        "search_financial_knowledge",
        "general",
    }

    tool_name = selection.get(
        "tool",
        "general",
    )

    arguments = selection.get(
        "arguments",
        {},
    )

    if not isinstance(arguments, dict):
        arguments = {}

    if tool_name not in allowed_tools:

        tool_name = "general"
        arguments = {}

    # --------------------------------
    # Secure portfolio ID
    # --------------------------------

    if tool_name in {
        "get_portfolio_summary",
        "get_sector_allocation",
    }:

        if portfolio_id is not None:

            arguments["portfolio_id"] = (
                portfolio_id
            )

    # --------------------------------
    # RAG query
    # --------------------------------

    if tool_name == "search_financial_knowledge":

        query = arguments.get(
            "query",
            message,
        )

        if not isinstance(query, str):
            query = message

        query = query.strip() or message

        # --------------------------------
        # Rewrite follow-up question
        # --------------------------------

        # Most follow-up messages are already self-contained. Only spend an
        # additional model call resolving references when the wording needs it.
        if conversation_history and re.search(
            r"\b(it|this|that|they|them|these|those|above)\b",
            query,
            flags=re.IGNORECASE,
        ):
            query = await rewrite_rag_query(
                message=query,
                conversation_history=conversation_history,
                gemini_service=gemini_service,
            )

        arguments["query"] = query

    # --------------------------------
    # Return updated graph state
    # --------------------------------

    return {
        **state,
        "tool_name": tool_name,
        "tool_arguments": arguments,
    }


# ============================================================
# TOOL NODE
# ============================================================

async def tool_node(
    state: FinGenieState,
    tool_executor,
) -> FinGenieState:

    tool_name = state.get(
        "tool_name",
        "general",
    )

    arguments = state.get(
        "tool_arguments",
        {},
    )

    user_id = state["user_id"]

    # --------------------------------
    # General questions
    # --------------------------------

    if tool_name == "general":

        return {
            **state,
            "tool_result": {},
            "tool_error": None,
            "sources": [],
        }

    # --------------------------------
    # Execute selected tool
    # --------------------------------

    try:

        result = await tool_executor.execute(
            tool_name=tool_name,
            arguments=arguments,
            user_id=user_id,
        )

    except Exception:

        return {
            **state,
            "tool_result": {},
            "tool_error": (
                "Unable to retrieve the "
                "requested information."
            ),
            "sources": [],
        }

    # --------------------------------
    # RAG sources
    # --------------------------------

    sources = []

    if (
        tool_name == "search_financial_knowledge"
        and isinstance(result, dict)
    ):

        sources = result.get(
            "sources",
            [],
        )

    return {
        **state,
        "tool_result": result,
        "tool_error": None,
        "sources": sources,
    }


# ============================================================
# RESPONSE NODE
# ============================================================

async def response_node(
    state: FinGenieState,
    gemini_service: GeminiService,
) -> FinGenieState:

    message = state["message"]

    tool_name = state.get(
        "tool_name",
        "general",
    )

    tool_result = state.get(
        "tool_result",
        {},
    )

    tool_error = state.get(
        "tool_error"
    )

    conversation_history = state.get(
        "conversation_history",
        [],
    )

    # --------------------------------
    # Format conversation history
    # --------------------------------

    if conversation_history:

        history_text = "\n".join(
            f"{item.get('role', 'user')}: "
            f"{item.get('content', '')}"
            for item in conversation_history
        )

    else:

        history_text = (
            "No previous conversation."
        )

    # --------------------------------
    # Handle tool error
    # --------------------------------

    if tool_error:

        tool_result = {
            "error": tool_error
        }

    # RAG has already generated a grounded response. Returning it directly
    # prevents a second, redundant model generation for document questions.
    if (
        tool_name == "search_financial_knowledge"
        and not tool_error
        and isinstance(tool_result, dict)
        and isinstance(tool_result.get("answer"), str)
    ):
        return {
            **state,
            "response": tool_result["answer"].strip(),
        }

    # --------------------------------
    # Final response prompt
    # --------------------------------

    prompt = f"""
You are FinGenie, an AI financial copilot.

Recent conversation:

{history_text}

Current user question:

{message}

Tool used:

{tool_name}

Verified information retrieved by the backend:

{tool_result}

Instructions:

1. Answer the user's question naturally.

2. Use the backend result as the source of
   truth for financial information.

3. Never invent financial numbers.

4. Do not claim information is current unless
   it was provided by the backend.

5. If the backend result does not contain
   enough information, clearly say so.

6. For RAG answers, use only information
   supported by the retrieved knowledge.

7. Keep the answer concise and understandable.

8. Do not mention internal implementation
   details such as tools, APIs, prompts,
   databases, embeddings, reranking,
   or vector stores.

9. Do not provide investment advice unless
   the retrieved information explicitly
   supports it.

Provide only the final answer.
"""

    response = (
        await gemini_service.generate_response(
            prompt
        )
    )

    return {
        **state,
        "response": response.strip(),
    }


# ============================================================
# ROUTE TOOL
# ============================================================

def route_tool(
    state: FinGenieState,
) -> str:

    tool_name = state.get(
        "tool_name",
        "general",
    )

    if tool_name in {
        "get_portfolio_summary",
        "get_sector_allocation",
        "get_market_data",
        "search_financial_knowledge",
    }:

        return "tool"

    return "response"
