import numpy as np
from typing import List, Dict, Any
from db.connection import SessionLocal, engine
from db.models import KnowledgeDocument
from embeddings.embedder import VectorEmbedder
from config.settings import settings

def cosine_similarity_vec(v1, v2):
    vec1 = np.array(v1, dtype=np.float32)
    vec2 = np.array(v2, dtype=np.float32)
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return float(np.dot(vec1, vec2) / (norm1 * norm2))

class VectorSearchService:
    """Performs cosine similarity search on knowledge_documents table for Postgres or SQLite."""

    def __init__(self):
        self.embedder = VectorEmbedder()

    def search(self, query: str, top_k: int = None) -> List[Dict[str, Any]]:
        if top_k is None:
            top_k = settings.TOP_K_RETRIEVAL

        query_vector = self.embedder.embed_text(query)
        session = SessionLocal()
        is_postgres = engine.dialect.name == "postgresql"

        try:
            if is_postgres:
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
            else:
                docs = session.query(KnowledgeDocument).all()
                scored_docs = []
                for doc in docs:
                    doc_vec = doc.embedding or []
                    sim = cosine_similarity_vec(query_vector, doc_vec) if doc_vec else 0.0
                    scored_docs.append({
                        "id": str(doc.id),
                        "content": doc.content,
                        "source_type": doc.source_type,
                        "source_id": doc.source_id,
                        "metadata": doc.doc_metadata or {},
                        "similarity": sim
                    })
                scored_docs.sort(key=lambda x: x["similarity"], reverse=True)
                return scored_docs[:top_k]
        finally:
            session.close()
