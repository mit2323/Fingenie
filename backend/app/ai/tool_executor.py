from app.ai.tools.rag_tool import RAGTool
from app.ai.tools.risk_tool import RiskTool

class ToolExecutor:

    def __init__(
        self,
        portfolio_tool,
        analytics_tool,
        market_tool,
        rag_tool,
        risk_tool,
    ):

        self.portfolio_tool = portfolio_tool
        self.analytics_tool = analytics_tool
        self.market_tool = market_tool
        self.rag_tool = rag_tool
        self.risk_tool = risk_tool

    async def execute(
        self,
        tool_name: str,
        arguments: dict,
        user_id: int,
    ):

        if not isinstance(arguments, dict):

            raise ValueError(
                "Tool arguments must be a dictionary."
            )

        # --------------------------------
        # Portfolio Summary
        # --------------------------------

        if tool_name == "get_portfolio_summary":

            portfolio_id = arguments.get(
                "portfolio_id"
            )

            if portfolio_id is None:

                raise ValueError(
                    "portfolio_id is required."
                )

            return await (
                self.portfolio_tool.execute(
                    portfolio_id=portfolio_id,
                    user_id=user_id,
                )
            )

        # --------------------------------
        # Sector Allocation
        # --------------------------------

        if tool_name == "get_sector_allocation":

            portfolio_id = arguments.get(
                "portfolio_id"
            )

            if portfolio_id is None:

                raise ValueError(
                    "portfolio_id is required."
                )

            return await (
                self.analytics_tool.execute(
                    portfolio_id=portfolio_id,
                    user_id=user_id,
                )
            )

        # --------------------------------
        # Market Data
        # --------------------------------

        if tool_name == "get_market_data":

            ticker = arguments.get(
                "ticker"
            )

            if not ticker:

                raise ValueError(
                    "ticker is required."
                )

            return await (
                self.market_tool.execute(
                    ticker=ticker,
                )
            )

        # --------------------------------
        # RAG
        # --------------------------------

        if tool_name == "search_financial_knowledge":

            query = arguments.get(
                "query"
            )

            if not query:

                raise ValueError(
                    "query is required."
                )

            return await (
                self.rag_tool.execute(
                    query=query,
                    user_id=user_id,
                )
            )

        # --------------------------------
        # Risk Analysis
        # --------------------------------

        if tool_name == "risk_analysis":

            portfolio_id = arguments.get(
                "portfolio_id"
            )

            if portfolio_id is None:

                raise ValueError(
                    "portfolio_id is required."
                )

            return await (
                self.risk_tool.execute(
                    portfolio_id=portfolio_id,
                    user_id=user_id,
                )
            )

        # --------------------------------
        # Unknown Tool
        # --------------------------------

        raise ValueError(
            f"Unknown tool: {tool_name}"
        )
