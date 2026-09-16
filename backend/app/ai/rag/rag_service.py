from pathlib import Path

from app.ai.rag.chunker import TextChunker
from app.ai.rag.document_loader import DocumentLoader
from app.ai.rag.embeddings import EmbeddingService
from app.ai.rag.retriever import Retriever
from app.ai.rag.vector_store import VectorStore
from app.ai.rag.reranker import Reranker

from app.services.gemini_service import GeminiService


class RAGService:

    def __init__(
        self,
        gemini_service: GeminiService | None = None,
    ):
        # -----------------------------------------
        # RAG Components
        # -----------------------------------------

        self.loader = DocumentLoader()

        self.chunker = TextChunker()

        self.embedding_service = (
            EmbeddingService()
        )

        self.vector_store = VectorStore()

        self.reranker = Reranker()

        self.retriever = Retriever(
            embedding_service=self.embedding_service,
            vector_store=self.vector_store,
            reranker=self.reranker,
        )

        self.gemini_service = gemini_service

    # =========================================
    # DOCUMENT INGESTION
    # =========================================

    def ingest_pdf(
        self,
        file_path: str,
        user_id: int,
        document_name: str | None = None,
    ) -> dict:

        # -----------------------------------------
        # 1. Get document name
        # -----------------------------------------

        document_name = document_name or Path(file_path).name

        # -----------------------------------------
        # 2. Check if already indexed
        # -----------------------------------------

        if self.vector_store.document_exists(
            document_name,
            user_id,
        ):

            return {
                "document": document_name,
                "chunks": 0,
                "status": "already_indexed",
                "message": (
                    "Document is already present "
                    "in the knowledge base."
                ),
            }

        # -----------------------------------------
        # 3. Load PDF
        # -----------------------------------------

        text = self.loader.load_pdf(
            file_path
        )

        # -----------------------------------------
        # 4. Split into chunks
        # -----------------------------------------

        chunks = self.chunker.split(
            text
        )

        if not chunks:
            raise ValueError(
                "No text could be extracted from PDF."
            )

        # -----------------------------------------
        # 5. Generate embeddings
        # -----------------------------------------

        embeddings = (
            self.embedding_service.embed(
                chunks
            )
        )

        # -----------------------------------------
        # 6. Prepare metadata
        # -----------------------------------------

        metadatas = [
            {
                "source": document_name,
                "chunk_index": index,
                "user_id": user_id,
            }
            for index in range(
                len(chunks)
            )
        ]

        # -----------------------------------------
        # 7. Create unique chunk IDs
        # -----------------------------------------

        ids = [
            f"{user_id}:{document_name}-{index}"
            for index in range(
                len(chunks)
            )
        ]

        # -----------------------------------------
        # 8. Store in ChromaDB
        # -----------------------------------------

        self.vector_store.add_documents(
            documents=chunks,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids,
        )

        # -----------------------------------------
        # 9. Return ingestion result
        # -----------------------------------------

        return {
            "document": document_name,
            "chunks": len(chunks),
            "status": "indexed",
            "message": (
                "Document successfully added "
                "to the knowledge base."
            ),
        }

    # =========================================
    # RETRIEVAL
    # =========================================

    def retrieve(
        self,
        query: str,
        user_id: int,
        top_k: int = 5,
        candidate_k: int = 10,
    ) -> list[dict]:

        return self.retriever.retrieve(
            query=query,
            user_id=user_id,
            top_k=top_k,
            candidate_k=candidate_k,
        )

    # =========================================
    # RAG QUESTION ANSWERING
    # =========================================

    async def answer(
        self,
        query: str,
        user_id: int,
        top_k: int = 3,
    ) -> dict:

        # -----------------------------------------
        # 1. Check Gemini service
        # -----------------------------------------

        if self.gemini_service is None:
            raise ValueError(
                "Gemini service is not configured."
            )

        # -----------------------------------------
        # 2. Retrieve relevant chunks
        # -----------------------------------------

        retrieved_chunks = self.retrieve(
            query=query,
            user_id=user_id,
            top_k=top_k,
            candidate_k=10,
        )

        # -----------------------------------------
        # 3. Handle no relevant results
        # -----------------------------------------

        if not retrieved_chunks:

            return {
                "answer": (
                    "I couldn't find relevant "
                    "information in the financial "
                    "knowledge base."
                ),
                "sources": [],
            }

        # -----------------------------------------
        # 4. Build context for Gemini
        # -----------------------------------------

        context_parts = []
        sources = []

        for index, item in enumerate(
            retrieved_chunks,
            start=1,
        ):

            content = item.get(
                "content",
                "",
            )

            metadata = item.get(
                "metadata",
                {},
            )

            source = metadata.get(
                "source",
                "Unknown",
            )

            chunk_index = metadata.get(
                "chunk_index",
                -1,
            )

            context_parts.append(
                f"""
SOURCE {index}

Document: {source}
Chunk: {chunk_index}

Content:
{content}
"""
            )

            sources.append(
                {
                    "source": source,
                    "chunk_index": chunk_index,
                }
            )

        context = "\n".join(
            context_parts
        )

        # -----------------------------------------
        # 5. Generate grounded answer
        # -----------------------------------------

        prompt = f"""
You are FinGenie's financial knowledge
assistant.

Answer the user's question using ONLY
the information contained in the provided
context.

USER QUESTION:
{query}

RETRIEVED CONTEXT:
{context}

IMPORTANT RULES:

1. Answer only from the retrieved context.

2. Do not use outside knowledge.

3. Do not invent financial facts, numbers,
   dates, regulations, or conclusions.

4. If the context does not contain enough
   information to answer the question,
   say that the information is not available
   in the provided knowledge base.

5. Prefer the most directly relevant source.

6. If multiple sources contain relevant
   information, combine them carefully.

7. Keep the answer concise and clear.

8. Do not mention retrieval, embeddings,
   reranking, Gemini, vector databases,
   or other internal implementation details.

9. Do not provide investment advice unless
   the retrieved context explicitly supports it.

Answer:
"""

        answer = (
            await self.gemini_service.generate_response(
                prompt
            )
        )

        # -----------------------------------------
        # 6. Return answer and sources
        # -----------------------------------------

        return {
            "answer": answer.strip(),
            "sources": sources,
        }
