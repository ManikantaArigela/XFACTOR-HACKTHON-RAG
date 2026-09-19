from typing import Dict, Any, Tuple
from config.settings import settings

FALLBACK_UNGROUNDED_MESSAGE = (
    "I don't have enough information to answer that from the available Arudhra Mobile Stores data."
)

class GroundingGuardrail:
    """Verifies retrieval evidence quality and enforces grounding thresholds."""

    def __init__(self, threshold: float = None):
        self.threshold = threshold if threshold is not None else settings.GROUNDING_THRESHOLD

    def evaluate_grounding(
        self,
        retrieval_result: Dict[str, Any],
        query_analysis: Dict[str, Any]
    ) -> Tuple[bool, str, float]:
        intent = query_analysis.get("intent", "product_search")

        # Conversational / Greetings and Store Info are always valid and grounded
        if intent in ["greeting", "store_info"]:
            return True, "", 1.0

        candidates = retrieval_result.get("candidates", [])
        max_similarity = retrieval_result.get("max_similarity", 0.0)
        has_structured_filters = retrieval_result.get("has_structured_filters", False)
        structured_matches_count = retrieval_result.get("structured_matches_count", 0)
        is_model_not_found = retrieval_result.get("is_model_not_found", False)

        # Rule 0: Adversarial / prompt injection rejection
        if query_analysis.get("is_adversarial"):
            print("[GUARDRAIL] Refusing adversarial / prompt injection query.")
            return False, FALLBACK_UNGROUNDED_MESSAGE, 0.0

        # Rule 0b: Unsupported domain queries (TVs, Refrigerators, Consoles, Policies)
        if query_analysis.get("is_unsupported"):
            print("[GUARDRAIL] Refusing unsupported product / domain query.")
            return False, FALLBACK_UNGROUNDED_MESSAGE, 0.0

        # Rule 1: Specific requested model is not in stock / catalog
        if is_model_not_found:
            brand = query_analysis.get("brand") or ""
            target_model = retrieval_result.get("target_model") or query_analysis.get("original_query")
            polite_msg = f"Sorry, we currently do not have the **{target_model}** in stock at Arudhra Mobile Stores, Pithapuram."
            alts = retrieval_result.get("suggested_alternatives", [])
            if alts:
                alt_names = [p.get("name") for p in alts if p.get("name")]
                if alt_names:
                    polite_msg += f"\n\nYou can explore our available {brand} models:\n" + "\n".join([f"• **{name}**" for name in alt_names[:3]])
            polite_msg += "\n\nPlease check our shop page or contact us to see more available mobiles!"
            return False, polite_msg, 0.0

        # Rule 2: If structured filters were explicitly requested (e.g. "Samsung under 10k")
        # and 0 products matched, the query cannot be grounded in existing store inventory.
        if has_structured_filters and structured_matches_count == 0:
            return False, FALLBACK_UNGROUNDED_MESSAGE, 0.0

        # Rule 3: If no candidates were retrieved at all
        if not candidates:
            return False, FALLBACK_UNGROUNDED_MESSAGE, 0.0

        # Rule 3b: If this is a catalog browse or category query with matched inventory candidates
        if (query_analysis.get("target_attribute") == "catalog_browse" or query_analysis.get("category")) and candidates:
            return True, "", max(max_similarity, 0.85)

        # Rule 4: Check maximum vector cosine similarity score against threshold
        if max_similarity < self.threshold:
            print(f"[GUARDRAIL] Low confidence score: {max_similarity:.4f} < threshold ({self.threshold})")
            return False, FALLBACK_UNGROUNDED_MESSAGE, max_similarity

        return True, "", max_similarity
