import json

from app.ai.prompts.system_prompt import SYSTEM_PROMPT
from app.ai.tool_executor import ToolExecutor
from app.services.gemini_service import GeminiService


class FinGenieAgent:

    def __init__(
        self,
        gemini_service: GeminiService,
        tool_executor: ToolExecutor,
    ):
        self.gemini_service = gemini_service
        self.tool_executor = tool_executor

    async def run(
        self,
        message: str,
        user_id: int,
        portfolio_id: int | None = None,
        conversation_history: list[dict] | None = None,
    ) -> dict:

        # ----------------------------------------
        # Conversation History
        # ----------------------------------------

        conversation_history = conversation_history or []

        history_text = self._format_history(
            conversation_history
        )

        # ----------------------------------------
        # Step 1: Ask Gemini to select a tool
        # ----------------------------------------

        tool_prompt = f"""
You are the tool-selection component of FinGenie,
an AI financial copilot.

Your job is to determine whether the user's question
requires one of FinGenie's backend tools.

Available tools:

1. get_portfolio_summary

Use this tool for:

- portfolio performance
- total investment
- portfolio value
- profit/loss
- portfolio returns
- holdings summary

2. get_sector_allocation

Use this tool for:

- sector allocation
- diversification
- sector exposure
- portfolio concentration

3. get_market_data

Use this tool for:

- current stock price
- 52-week high
- 52-week low
- market capitalization
- trading volume
- PE ratio
- dividend yield
- current stock information

4. search_financial_knowledge

Use this tool for:

- financial concepts
- investment principles
- investor education
- financial regulations
- information contained in financial documents
- questions requiring information from the financial knowledge base

5. general

Use this when the question doesn't require
a backend financial tool.

IMPORTANT:

Use the conversation history to understand
follow-up questions.

For example:

Previous:
User: What is the current price of TCS?

Current:
User: What is its 52-week high?

You should understand that "its" refers to TCS.

Return ONLY valid JSON.

For get_portfolio_summary:

{{
    "tool": "get_portfolio_summary",
    "arguments": {{
        "portfolio_id": <portfolio_id>
    }}
}}

For get_sector_allocation:

{{
    "tool": "get_sector_allocation",
    "arguments": {{
        "portfolio_id": <portfolio_id>
    }}
}}

For get_market_data:

{{
    "tool": "get_market_data",
    "arguments": {{
        "ticker": "TCS"
    }}
}}

For search_financial_knowledge:

{{
    "tool": "search_financial_knowledge",
    "arguments": {{
        "query": "user's question"
    }}
}}

For general:

{{
    "tool": "general",
    "arguments": {{}}
}}

Authenticated user's portfolio ID:

{portfolio_id}

Recent conversation history:

{history_text}

Current user question:

{message}
"""

        selection_response = (
            await self.gemini_service.generate_response(
                tool_prompt
            )
        )

        selection = self._parse_json(
            selection_response
        )

        tool_name = selection.get(
            "tool",
            "general",
        )

        arguments = selection.get(
            "arguments",
            {},
        )

        # ----------------------------------------
        # Step 2: Validate Tool Selection
        # ----------------------------------------

        allowed_tools = {
            "get_portfolio_summary",
            "get_sector_allocation",
            "get_market_data",
            "search_financial_knowledge",
            "general",
        }

        if tool_name not in allowed_tools:

            tool_name = "general"
            arguments = {}

        # ----------------------------------------
        # Step 3: Prepare Tool Arguments
        # ----------------------------------------

        if tool_name in {
            "get_portfolio_summary",
            "get_sector_allocation",
        }:

            # Never trust Gemini to choose which
            # user's portfolio can be accessed.
            #
            # The authenticated portfolio_id comes
            # from the API request.

            if portfolio_id is None:

                return {
                    "intent": tool_name,
                    "response": (
                        "Please provide a portfolio ID "
                        "so I can analyze your portfolio."
                    ),
                }

            arguments["portfolio_id"] = portfolio_id

        # ----------------------------------------
        # Step 3B: Prepare RAG Arguments
        # ----------------------------------------

        if tool_name == "search_financial_knowledge":

            # Never allow Gemini to send an empty
            # or invalid RAG query.

            rag_query = arguments.get(
                "query",
                message,
            )

            if not isinstance(
                rag_query,
                str,
            ):
                rag_query = message

            rag_query = rag_query.strip()

            if not rag_query:

                rag_query = message

            arguments["query"] = rag_query

        # ----------------------------------------
        # Step 4: Execute Backend Tool
        # ----------------------------------------

        financial_context = {}

        if tool_name != "general":

            try:

                financial_context = (
                    await self.tool_executor.execute(
                        tool_name=tool_name,
                        arguments=arguments,
                        user_id=user_id,
                    )
                )

            except Exception:

                return {
                    "intent": tool_name,
                    "response": (
                        "I couldn't retrieve the "
                        "requested financial information "
                        "right now."
                    ),
                }


        # ----------------------------------------
        # Step 5: Prepare RAG Sources
        # ----------------------------------------

        sources = []

        if (
            tool_name == "search_financial_knowledge"
            and isinstance(financial_context, dict)
        ):

            sources = financial_context.get(
                "sources",
                [],
            )


        # ----------------------------------------
        # Step 6: Generate Final Gemini Response
        # ----------------------------------------

        final_prompt = f"""
        {SYSTEM_PROMPT}

        You are FinGenie, an AI financial copilot.

        Recent conversation:

        {history_text}

        Current user question:

        {message}

        Tool used:

        {tool_name}

        Verified financial data retrieved by the backend:

        {financial_context}

        Instructions:

        1. Answer the user's current question naturally.

        2. Use the verified backend data as the
        source of truth for financial numbers.

        3. Never invent:

        - stock prices
        - portfolio values
        - returns
        - profit/loss
        - market capitalization
        - PE ratios
        - sector percentages
        - other financial figures.

        4. Do not claim that information is current unless
        it was provided by the backend tool.

        5. Use conversation history when the user refers
        to something previously discussed.

        6. If the backend data does not contain the
        requested information, clearly say that the
        information is unavailable.

        7. For financial knowledge retrieved from the
        knowledge base, answer only using the retrieved
        information.

        8. Do not invent facts that are not supported by
        the retrieved financial knowledge.

        9. Keep the answer concise and understandable.

        10. Do not mention internal implementation details
            such as tools, APIs, Gemini, prompts, or
            database queries.

        Provide only the final answer to the user.
        """

        final_response = (
            await self.gemini_service.generate_response(
                final_prompt
            )
        )


        # ----------------------------------------
        # Step 7: Return Agent Result
        # ----------------------------------------

        return {
            "intent": tool_name,
            "response": final_response,
            "sources": sources,
        }
    # ============================================
    # Helper: Format Conversation History
    # ============================================

    @staticmethod
    def _format_history(
        conversation_history: list[dict],
    ) -> str:

        if not conversation_history:
            return "No previous conversation."

        formatted_messages = []

        for item in conversation_history:

            role = item.get(
                "role",
                "user",
            )

            content = item.get(
                "content",
                "",
            )

            formatted_messages.append(
                f"{role}: {content}"
            )

        return "\n".join(
            formatted_messages
        )

    # ============================================
    # Helper: Parse Gemini JSON
    # ============================================

    @staticmethod
    def _parse_json(
        response: str,
    ) -> dict:

        response = response.strip()

        # Remove Markdown code fences if Gemini
        # happens to return them.

        if response.startswith("```"):

            response = (
                response
                .replace("```json", "")
                .replace("```", "")
                .strip()
            )

        try:

            return json.loads(response)

        except json.JSONDecodeError:

            return {
                "tool": "general",
                "arguments": {},
            }