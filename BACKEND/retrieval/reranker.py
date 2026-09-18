from typing import List, Dict, Any

class CandidateReranker:
    """Reranks candidate retrieval results based on user preferences and exact score metrics."""

    def rerank(self, candidates: List[Dict[str, Any]], query_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        if not candidates:
            return []

        reqs = query_analysis.get("requirements", [])
        
        # If user asked for cheapest/budget phone, sort candidates by price ascending
        if "budget" in reqs or "cheap" in query_analysis.get("original_query", "").lower():
            # Separate candidates with valid prices
            priced = [c for c in candidates if c.get("product", {}).get("price") is not None]
            unpriced = [c for c in candidates if c.get("product", {}).get("price") is None]
            
            priced.sort(key=lambda x: x["product"]["price"])
            return priced + unpriced

        # Default: keep ranked by highest similarity score
        candidates.sort(key=lambda x: x.get("similarity_score", 0.0), reverse=True)
        return candidates
