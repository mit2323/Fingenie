from app.ai.rag.rag_service import RAGService
from app.services.gemini_service import GeminiService


async def main():

    gemini_service = GeminiService()

    rag = RAGService(
        gemini_service=gemini_service
    )

    result = await rag.answer(
        query=(
            "What are the important principles "
            "of diversification?"
        ),
        user_id=1,
        top_k=3,
    )

    print("\nANSWER:")
    print(result["answer"])

    print("\nSOURCES:")

    for source in result["sources"]:
        print(source)


if __name__ == "__main__":

    import asyncio

    asyncio.run(main())
