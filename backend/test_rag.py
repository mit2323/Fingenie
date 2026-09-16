from app.ai.rag.rag_service import RAGService


def main():

    rag = RAGService()

    result = rag.ingest_pdf(
        "data/documents/sebi_investor_guidelines.pdf",
        user_id=1,
    )

    print("\nIngestion result:")
    print(result)

    results = rag.retrieve(
        query=(
            "What are the important principles "
            "of diversification?"
        ),
        user_id=1,
        top_k=3,
    )

    print("\nRetrieved results:")

    for index, item in enumerate(
        results,
        start=1,
    ):

        print(
            f"\n--- Result {index} ---"
        )

        print(
            "Source:",
            item["metadata"],
        )

        print(
            item["content"][:700]
        )


if __name__ == "__main__":
    main()
