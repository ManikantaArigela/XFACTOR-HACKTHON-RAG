from typing import List, Dict, Any
from retrieval.vector_search import VectorSearchService
from retrieval.structured_search import StructuredSearchService
from config.settings import settings

class HybridSearchService:
    """Combines relational SQL search and pgvector semantic similarity search."""

    def __init__(self):
        self.vector_search = VectorSearchService()
        self.structured_search = StructuredSearchService()

    def hybrid_search(
        self,
        query_analysis: Dict[str, Any],
        top_k: int = None
    ) -> Dict[str, Any]:
        if top_k is None:
            top_k = settings.TOP_K_RETRIEVAL

        brand = query_analysis.get("brand")
        max_price = query_analysis.get("max_price")
        min_price = query_analysis.get("min_price")
        ram = query_analysis.get("ram")
        storage = query_analysis.get("storage")
        category = query_analysis.get("category")
        semantic_query = query_analysis.get("semantic_query") or query_analysis.get("original_query")

        # 1. Execute Structured SQL Search
        has_structured_filters = any(v is not None for v in [brand, max_price, min_price, ram, storage])
        structured_products = []
        if has_structured_filters:
            structured_products = self.structured_search.search(
                brand=brand,
                max_price=max_price,
                min_price=min_price,
                ram=ram,
                storage=storage,
                category=category
            )

        # 2. Execute Semantic pgvector Search
        vector_docs = self.vector_search.search(query=semantic_query, top_k=top_k)

        # 3. Combine & Deduplicate Results
        max_vector_sim = max([doc["similarity"] for doc in vector_docs], default=0.0)

        # Map vector documents by post_id
        doc_map = {doc["source_id"]: doc for doc in vector_docs}
        
        candidates = []
        seen_source_ids = set()

        # Add structured match products
        for prod in structured_products:
            source_id = prod.get("source_id")
            doc = doc_map.get(source_id)
            
            sim_score = doc["similarity"] if doc else max(0.50, max_vector_sim)
            
            candidates.append({
                "product": prod,
                "doc_content": doc["content"] if doc else f"Product: {prod['name']}, Brand: {prod['brand']}, Price: ₹{prod['price']}, Specs: {prod['specifications']}",
                "source_url": doc["metadata"].get("post_url") if doc else None,
                "similarity_score": sim_score,
                "matched_by": "structured_sql"
            })
            if source_id:
                seen_source_ids.add(source_id)

        # Add remaining semantic vector documents
        for doc in vector_docs:
            source_id = doc["source_id"]
            if source_id not in seen_source_ids:
                candidates.append({
                    "product": {
                        "name": doc["metadata"].get("brand", "Mobile Product"),
                        "brand": doc["metadata"].get("brand"),
                        "price": doc["metadata"].get("price"),
                        "ram": doc["metadata"].get("ram"),
                        "storage": doc["metadata"].get("storage")
                    },
                    "doc_content": doc["content"],
                    "source_url": doc["metadata"].get("post_url"),
                    "similarity_score": doc["similarity"],
                    "matched_by": "vector_pgvector"
                })
                seen_source_ids.add(source_id)

        # Sort combined candidates by similarity score descending
        candidates.sort(key=lambda x: x["similarity_score"], reverse=True)

        return {
            "candidates": candidates[:top_k],
            "max_similarity": max([c["similarity_score"] for c in candidates], default=0.0),
            "structured_matches_count": len(structured_products),
            "vector_matches_count": len(vector_docs),
            "has_structured_filters": has_structured_filters
        }
