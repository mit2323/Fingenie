import chromadb


class VectorStore:

    def __init__(
        self,
        collection_name: str = "financial_documents",
    ):

        self.client = chromadb.PersistentClient(
            path="./data/chroma"
        )

        self.collection = (
            self.client.get_or_create_collection(
                name=collection_name
            )
        )

    # =========================================
    # ADD DOCUMENTS
    # =========================================

    def add_documents(
        self,
        documents: list[str],
        embeddings: list[list[float]],
        metadatas: list[dict],
        ids: list[str],
    ):

        self.collection.add(
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids,
        )

    # =========================================
    # CHECK DOCUMENT
    # =========================================

    def document_exists(
        self,
        document_name: str,
        user_id: int,
    ) -> bool:

        results = self.collection.get(
            where={
                "$and": [
                    {"source": document_name},
                    {"user_id": user_id},
                ]
            },
            limit=1,
        )

        ids = results.get(
            "ids",
            [],
        )

        return len(ids) > 0

    # =========================================
    # SEARCH
    # =========================================

    def search(
        self,
        query_embedding: list[float],
        user_id: int,
        top_k: int = 5,
    ):

        return self.collection.query(
            query_embeddings=[
                query_embedding
            ],
            where={"user_id": user_id},
            n_results=top_k,
            include=[
                "documents",
                "metadatas",
                "distances",
            ],
        )
