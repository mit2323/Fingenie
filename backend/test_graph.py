import asyncio

from app.ai.graph.graph import (
    create_fingenie_graph,
)

from app.ai.tool_executor import ToolExecutor

from app.ai.tools.analytics_tool import (
    AnalyticsTool,
)

from app.ai.tools.market_tool import (
    MarketTool,
)

from app.ai.tools.portfolio_tool import (
    PortfolioTool,
)

from app.ai.tools.rag_tool import (
    RAGTool,
)

from app.ai.rag.rag_service import (
    RAGService,
)

from app.services.gemini_service import (
    GeminiService,
)


async def main():

    # --------------------------------
    # Services
    # --------------------------------

    gemini_service = GeminiService()

    # --------------------------------
    # Tools
    # --------------------------------

    # For this isolated graph test,
    # portfolio/analytics/market services
    # are not required yet.
    #
    # We will connect the real dependencies
    # when integrating the graph into ChatService.

    rag_service = RAGService(
        gemini_service=gemini_service,
    )

    rag_tool = RAGTool(
        rag_service_factory=lambda: rag_service,
    )

    # --------------------------------
    # Temporary ToolExecutor
    # --------------------------------

    tool_executor = ToolExecutor(
        portfolio_tool=None,
        analytics_tool=None,
        market_tool=None,
        rag_tool=rag_tool,
        risk_tool=None,
    )

    # --------------------------------
    # Create graph
    # --------------------------------

    graph = create_fingenie_graph(
        gemini_service=gemini_service,
        tool_executor=tool_executor,
    )

    # --------------------------------
    # Initial state
    # --------------------------------

    initial_state = {
        "message": (
            "What is the fee for applying "
            "for informal guidance?"
        ),
        "user_id": 1,
        "portfolio_id": None,
        "conversation_history": [],
    }

    # --------------------------------
    # Run graph
    # --------------------------------

    result = await graph.ainvoke(
        initial_state
    )

    print("\n")
    print("=" * 60)
    print("LANGGRAPH RESULT")
    print("=" * 60)

    print(
        "Tool:",
        result.get("tool_name"),
    )

    print(
        "Arguments:",
        result.get("tool_arguments"),
    )

    print(
        "Response:",
        result.get("response"),
    )

    print(
        "Sources:",
        result.get("sources"),
    )


if __name__ == "__main__":
    asyncio.run(main())
