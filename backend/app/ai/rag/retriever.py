from app.ai.rag.embeddings import EmbeddingService
from app.ai.rag.reranker import Reranker
from app.ai.rag.vector_store import VectorStore


class Retriever:

    def __init__(
        self,
        embedding_service: EmbeddingService,
        vector_store: VectorStore,
        reranker: Reranker,
    ):
        self.embedding_service = embedding_service
        self.vector_store = vector_store
        self.reranker = reranker

    def retrieve(
        self,
        query: str,
        user_id: int,
        top_k: int = 5,
        candidate_k: int = 10,
    ) -> list[dict]:

        # -----------------------------------------
        # 1. Validate query
        # -----------------------------------------

        if not query or not query.strip():
            return []

        query = query.strip()

        # -----------------------------------------
        # 2. Create query embedding
        # -----------------------------------------

        query_embedding = (
            self.embedding_service.embed(
                [query]
            )[0]
        )

        # -----------------------------------------
        # 3. Vector search
        # -----------------------------------------

        results = self.vector_store.search(
            query_embedding=query_embedding,
            user_id=user_id,
            top_k=candidate_k,
        )

        documents = results.get(
            "documents",
            [[]],
        )[0]

        metadatas = results.get(
            "metadatas",
            [[]],
        )[0]

        distances = results.get(
            "distances",
            [[]],
        )[0]

        candidates = []

        for document, metadata, distance in zip(
            documents,
            metadatas,
            distances,
        ):
            candidates.append(
                {
                    "content": document,
                    "metadata": metadata,
                    "distance": distance,
                }
            )

        if not candidates:
            return []

        # -----------------------------------------
        # 4. Rerank
        # -----------------------------------------

        ranked_results = self.reranker.rerank(
            query=query,
            documents=candidates,
            top_k=top_k,
        )

        if not ranked_results:
            return []

        # -----------------------------------------
        # 5. Relevance check
        # -----------------------------------------

        best_score = ranked_results[0].get(
            "rerank_score",
            -999,
        )

        # Difference between best and worst
        # returned result.
        worst_score = ranked_results[-1].get(
            "rerank_score",
            -999,
        )

        score_gap = (
            best_score - worst_score
        )

        # -----------------------------------------
        # 6. Reject obviously weak retrieval
        # -----------------------------------------

        # If the best result itself is extremely
        # weak, don't send unrelated content to
        # Gemini.

        if best_score < -8.0:
            return []

        # If all results are very close together
        # and the best result is weak, retrieval
        # is probably uncertain.

        if (
            best_score < -3.0
            and score_gap < 2.0
        ):
            return []

        # -----------------------------------------
        # 7. Return relevant results
        # -----------------------------------------

        return ranked_results[:top_k]
