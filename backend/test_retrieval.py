from app.ai.rag.rag_service import RAGService


QUESTIONS = [
    "What is the fee for applying for informal guidance?",
    "How long can the Department take to dispose of an application?",
    "Who can apply for informal guidance?",
    "What are the two forms of informal guidance?",
    "How long can confidential treatment be requested?",
    "What happens if an application is rejected?",
    "What is diversification?",
]


def main():

    rag = RAGService()

    print("\n" + "=" * 100)
    print("FinGenie RAG Evaluation")
    print("=" * 100)

    for question in QUESTIONS:

        print("\n" + "=" * 100)
        print(f"QUESTION:\n{question}")
        print("=" * 100)

        try:

            results = rag.retrieve(
                query=question,
                user_id=1,
                top_k=3,
                candidate_k=10,
            )

        except Exception as exc:

            print(f"\n❌ RETRIEVAL ERROR: {exc}")
            continue

        if not results:

            print("\n❌ NO RELEVANT RESULTS FOUND")
            continue

        print(
            f"\n✅ RESULTS RETURNED: "
            f"{len(results)}"
        )

        for index, result in enumerate(
            results,
            start=1,
        ):

            print(
                f"\n--- RESULT {index} ---"
            )

            print(
                "VECTOR DISTANCE:",
                result.get(
                    "distance"
                ),
            )

            print(
                "RERANK SCORE:",
                result.get(
                    "rerank_score"
                ),
            )

            print(
                "SOURCE:",
                result.get(
                    "metadata"
                ),
            )

            content = result.get(
                "content",
                "",
            )

            print(
                "\nCONTENT:"
            )

            print(
                content[:1500]
            )


if __name__ == "__main__":
    main()
