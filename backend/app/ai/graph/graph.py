from langgraph.graph import (
    StateGraph,
    START,
    END,
)

from app.ai.graph.state import FinGenieState

from app.ai.graph.nodes import (
    agent_node,
    tool_node,
    response_node,
    route_tool,
)

from app.ai.tool_executor import ToolExecutor
from app.services.gemini_service import GeminiService


def create_fingenie_graph(
    gemini_service: GeminiService,
    tool_executor: ToolExecutor,
):

    graph = StateGraph(
        FinGenieState
    )

    # --------------------------------
    # Agent node
    # --------------------------------

    async def run_agent(
        state: FinGenieState,
    ):

        return await agent_node(
            state,
            gemini_service,
        )

    # --------------------------------
    # Tool node
    # --------------------------------

    async def run_tool(
        state: FinGenieState,
    ):

        return await tool_node(
            state,
            tool_executor,
        )

    # --------------------------------
    # Response node
    # --------------------------------

    async def run_response(
        state: FinGenieState,
    ):

        return await response_node(
            state,
            gemini_service,
        )

    # --------------------------------
    # Register nodes
    # --------------------------------

    graph.add_node(
        "agent",
        run_agent,
    )

    graph.add_node(
        "tool",
        run_tool,
    )

    graph.add_node(
        "response",
        run_response,
    )

    # --------------------------------
    # START → Agent
    # --------------------------------

    graph.add_edge(
        START,
        "agent",
    )

    # --------------------------------
    # Agent → Tool / Response
    # --------------------------------

    graph.add_conditional_edges(
        "agent",
        route_tool,
        {
            "tool": "tool",
            "response": "response",
        },
    )

    # --------------------------------
    # Tool → Response
    # --------------------------------

    graph.add_edge(
        "tool",
        "response",
    )

    # --------------------------------
    # Response → END
    # --------------------------------

    graph.add_edge(
        "response",
        END,
    )

    # --------------------------------
    # Compile
    # --------------------------------

    return graph.compile()