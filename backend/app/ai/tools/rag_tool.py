class RAGTool:

    def __init__(
        self,
        rag_service_factory,
    ):
        self.rag_service_factory = rag_service_factory

    async def execute(
        self,
        query: str,
        user_id: int,
    ):

        return await self.rag_service_factory().answer(
            query=query,
            user_id=user_id,
            top_k=5,
        )
