from typing import Dict, Any, List, Optional
from .query_analyzer import QueryAnalyzer
from .retrieval.hybrid_search import HybridSearchService
from .retrieval.reranker import CandidateReranker
from .retrieval.vector_search import VectorSearchService
from .retrieval.structured_search import StructuredSearchService
from .guardrails.grounding import GroundingGuardrail, FALLBACK_UNGROUNDED_MESSAGE
from .generation.generator import ResponseGenerator
from .generation.context_builder import ContextBuilder
from .embeddings.embedder import VectorEmbedder

class RAGChatbotService:
    """Unified, self-contained AI RAG Chatbot Service for Arudhra Mobile Stores.
    Operates 100% locally with high precision and zero external agent API keys."""

    def __init__(self):
        self.query_analyzer = QueryAnalyzer()
        self.hybrid_search = HybridSearchService()
        self.reranker = CandidateReranker()
        self.grounding_guardrail = GroundingGuardrail()
        self.generator = ResponseGenerator()

    def answer_query(self, user_message: str, history: Optional[List[Dict[str, str]]] = None) -> Dict[str, Any]:
        user_message = (user_message or "").strip()
        if not user_message:
            return {
                "answer": "Please provide a valid question or query.",
                "products": [],
                "sources": [],
                "grounded": False,
                "confidence": 0.0
            }

        # 1. Query Analysis with multi-turn conversation history
        query_analysis = self.query_analyzer.analyze(user_message, history=history)
        intent = query_analysis.get("intent", "product_search")

        # 1a. Handle Greeting
        if intent == "greeting":
            return {
                "answer": self.generator.generate_greeting(),
                "products": [],
                "sources": [],
                "grounded": True,
                "confidence": 1.0
            }

        # 1b. Handle Store Info
        if intent == "store_info":
            return {
                "answer": self.generator.generate_store_info(),
                "products": [],
                "sources": [],
                "grounded": True,
                "confidence": 1.0
            }

        # 2. Hybrid Retrieval (Relational SQL + semantic embeddings)
        retrieval_result = self.hybrid_search.hybrid_search(query_analysis)
        candidates = retrieval_result.get("candidates", [])

        # 3. Candidate Reranking
        ranked_candidates = self.reranker.rerank(candidates, query_analysis)

        # 4. Grounding Evaluation
        is_grounded, fallback_msg, confidence = self.grounding_guardrail.evaluate_grounding(
            retrieval_result, query_analysis
        )

        if not is_grounded:
            return {
                "answer": fallback_msg,
                "products": [],
                "sources": [],
                "grounded": False,
                "confidence": float(confidence)
            }

        # 5. Query-Targeted Zero-Hallucination Local Answer Generation
        answer = self.generator.generate_response(
            user_message,
            ranked_candidates,
            conversation_history=history,
            query_analysis=query_analysis
        )

        # 6. Build Clean, Strictly Relevant Product & Source Attachments
        products_payload = []
        sources_payload = []
        seen_sources = set()
        seen_names = set()

        is_specific = query_analysis.get("is_specific_model", False)
        tokens = query_analysis.get("model_tokens", [])
        target_attr = query_analysis.get("target_attribute", "general")

        # For specific queries (e.g. asking specifically about charging/battery/price for 1 phone),
        # only attach the top matching product rather than cluttering the chat with 5 products
        max_products_to_attach = 1 if (is_specific and target_attr in ["price", "battery_charging", "camera", "ram_storage"]) else 4

        for candidate in ranked_candidates:
            prod = candidate.get("product", {})
            prod_name = prod.get("name") or ""
            if not prod_name or prod_name in seen_names:
                continue

            # Strict gating for specific model queries
            if is_specific and tokens:
                if not all(tok in prod_name.lower() for tok in tokens):
                    continue

            seen_names.add(prod_name)
            poster_img = prod.get("poster_image_path") or candidate.get("poster_image_path") or prod.get("image_path")
            
            if len(products_payload) < max_products_to_attach:
                products_payload.append({
                    "id": prod.get("id"),
                    "name": prod_name,
                    "brand": prod.get("brand"),
                    "price": float(prod["price"]) if prod.get("price") is not None else None,
                    "ram": prod.get("ram"),
                    "storage": prod.get("storage"),
                    "image_path": prod.get("image_path"),
                    "poster_image_path": poster_img
                })

            source_url = candidate.get("source_url")
            if source_url and source_url not in seen_sources:
                seen_sources.add(source_url)
                sources_payload.append({
                    "source_type": "instagram",
                    "source_url": source_url,
                    "poster_image_path": poster_img
                })

        return {
            "answer": answer,
            "products": products_payload,
            "sources": sources_payload,
            "grounded": True,
            "confidence": round(float(confidence), 4)
        }

rag_service = RAGChatbotService()

__all__ = [
    "RAGChatbotService",
    "rag_service",
    "QueryAnalyzer",
    "HybridSearchService",
    "CandidateReranker",
    "VectorSearchService",
    "StructuredSearchService",
    "GroundingGuardrail",
    "ResponseGenerator",
    "ContextBuilder",
    "VectorEmbedder",
    "FALLBACK_UNGROUNDED_MESSAGE"
]
