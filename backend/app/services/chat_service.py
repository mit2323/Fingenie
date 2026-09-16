from app.ai.graph.graph import create_fingenie_graph

from app.ai.tool_executor import ToolExecutor

from app.ai.tools.analytics_tool import AnalyticsTool
from app.ai.tools.market_tool import MarketTool
from app.ai.tools.portfolio_tool import PortfolioTool
from app.ai.tools.rag_tool import RAGTool
from app.ai.tools.risk_tool import RiskTool

from app.repositories.conversation_repository import (
    ConversationRepository,
)

from app.schemas.chat import (
    ChatRequest,
    ChatResponse,
)

from app.services.analytics.risk_analysis_service import (
    RiskAnalysisService,
)


class ChatService:

    def __init__(
        self,
        portfolio_summary_service,
        allocation_service,
        market_service,
        conversation_repository: ConversationRepository,
        gemini_service,
        rag_service_factory,
    ):



        portfolio_tool = PortfolioTool(
            summary_service=portfolio_summary_service,
        )



        analytics_tool = AnalyticsTool(
            allocation_service=allocation_service,
        )

        market_tool = MarketTool(
            market_service=market_service,
        )


        rag_tool = RAGTool(
            rag_service_factory=rag_service_factory,
        )


        risk_analysis_service = (
            RiskAnalysisService(
                allocation_service=allocation_service,
            )
        )

        risk_tool = RiskTool(
            risk_analysis_service=(
                risk_analysis_service
            ),
        )


        tool_executor = ToolExecutor(
            portfolio_tool=portfolio_tool,
            analytics_tool=analytics_tool,
            market_tool=market_tool,
            rag_tool=rag_tool,
            risk_tool=risk_tool,
        )



        self.graph = create_fingenie_graph(
            gemini_service=gemini_service,
            tool_executor=tool_executor,
        )


        self.conversation_repository = (
            conversation_repository
        )

    # CHAT
    async def chat(
        self,
        request: ChatRequest,
        user_id: int,
    ) -> ChatResponse:

        # Get or Create Conversation

        if request.conversation_id is None:

            conversation = (
                await self.conversation_repository
                .create_conversation(
                    user_id=user_id,
                    title=request.message[:50],
                )
            )

        else:
            conversation = (
                await self.conversation_repository
                .get_by_id(
                    conversation_id=(
                        request.conversation_id
                    ),
                    user_id=user_id,
                )
            )

            if conversation is None:

                raise ValueError(
                    "Conversation not found."
                )

        # Load Recent Conversation History


        messages = (
            await self.conversation_repository
            .get_recent_messages(
                conversation_id=conversation.id,
                limit=10,
            )
        )

        conversation_history = [
            {
                "role": message.role,
                "content": message.content,
            }
            for message in messages
        ]

        # Save User Message
        await self.conversation_repository.add_message(
            conversation_id=conversation.id,
            role="user",
            content=request.message,
        )

        # Initial LangGraph State

        initial_state = {
            "message": request.message,
            "user_id": user_id,
            "portfolio_id": request.portfolio_id,
            "conversation_history": (
                conversation_history
            ),
        }

        # Run LangGraph
        result = await self.graph.ainvoke(
            initial_state
        )
        # Get Final Response

        response = result.get(
            "response",
            "I was unable to generate a response.",
        )

        # Save Assistant Response

        await self.conversation_repository.add_message(
            conversation_id=conversation.id,
            role="assistant",
            content=response,
        )

        # Get RAG Sources
        sources = result.get(
            "sources",
            [],
        )
        # Return API Response

        return ChatResponse(
            message=response,
            intent=result.get(
                "tool_name",
                "general",
            ),
            conversation_id=conversation.id,
            sources=sources,
        )
