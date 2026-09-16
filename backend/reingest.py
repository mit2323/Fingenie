from app.ai.rag.rag_service import RAGService


def main():

    rag = RAGService()

    result = rag.ingest_pdf(
        "data/documents/sebi_investor_guidelines.pdf"
    )

    print(result)


if __name__ == "__main__":
    main()