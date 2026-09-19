import re
from typing import List, Dict, Any

class CandidateReranker:
    """Reranks candidate retrieval results based on user preferences, exact token matches, and price metrics."""

    def rerank(self, candidates: List[Dict[str, Any]], query_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        if not candidates:
            return []

        tokens = query_analysis.get("model_tokens", [])
        is_specific = query_analysis.get("is_specific_model", False)
        reqs = query_analysis.get("requirements", [])
        original_lower = query_analysis.get("original_query", "").lower()

        # 1. Exact model match boosting
        if is_specific and tokens:
            exact_matches = []
            other_matches = []
            for c in candidates:
                prod_name = (c.get("product", {}).get("name") or "").lower()
                if all(tok in prod_name for tok in tokens):
                    # Boost similarity for exact match
                    c["similarity_score"] = max(c.get("similarity_score", 0.0), 0.99)
                    exact_matches.append(c)
                else:
                    other_matches.append(c)
            candidates = exact_matches + other_matches

        # 2. Budget / cheap queries: sort priced items ascending
        if "budget" in reqs or "cheap" in original_lower or query_analysis.get("target_attribute") == "price":
            # For general budget searches (not specific model queries)
            if not is_specific:
                priced = [c for c in candidates if c.get("product", {}).get("price") is not None]
                unpriced = [c for c in candidates if c.get("product", {}).get("price") is None]
                priced.sort(key=lambda x: x["product"]["price"])
                return priced + unpriced

        # 3. Default: sort by similarity score descending
        candidates.sort(key=lambda x: x.get("similarity_score", 0.0), reverse=True)
        return candidates
