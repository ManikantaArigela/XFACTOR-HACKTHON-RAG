from typing import List, Dict, Any
from db.connection import SessionLocal
from db.models import KnowledgeDocument
from embeddings.embedder import VectorEmbedder
from config.settings import settings

class VectorSearchService:
    """Performs pgvector cosine similarity search on knowledge_documents table."""

    def __init__(self):
        self.embedder = VectorEmbedder()

    def search(self, query: str, top_k: int = None) -> List[Dict[str, Any]]:
        if top_k is None:
            top_k = settings.TOP_K_RETRIEVAL

        query_vector = self.embedder.embed_text(query)
        session = SessionLocal()

        try:
            # Calculate cosine similarity: 1 - cosine distance (1 - (embedding <=> query_vector))
            similarity_expr = (1 - KnowledgeDocument.embedding.cosine_distance(query_vector)).label("similarity")

            results = (
                session.query(KnowledgeDocument, similarity_expr)
                .order_by(KnowledgeDocument.embedding.cosine_distance(query_vector).asc())
                .limit(top_k)
                .all()
            )

            retrieved_docs = []
            for doc, sim in results:
                retrieved_docs.append({
                    "id": str(doc.id),
                    "content": doc.content,
                    "source_type": doc.source_type,
                    "source_id": doc.source_id,
                    "metadata": doc.doc_metadata or {},
                    "similarity": float(sim) if sim is not None else 0.0
                })

            return retrieved_docs
        finally:
            session.close()
