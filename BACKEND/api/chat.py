from flask import Blueprint, request, jsonify
from generation.query_analyzer import QueryAnalyzer
from retrieval.hybrid_search import HybridSearchService
from retrieval.reranker import CandidateReranker
from guardrails.grounding import GroundingGuardrail
from generation.generator import ResponseGenerator

chat_bp = Blueprint("chat_bp", __name__)

query_analyzer = QueryAnalyzer()
hybrid_search = HybridSearchService()
reranker = CandidateReranker()
grounding_guardrail = GroundingGuardrail()
generator = ResponseGenerator()

@chat_bp.route("/api/chat", methods=["POST"])
def chat_endpoint():
    data = request.get_json(silent=True) or {}
    user_message = data.get("message", "").strip()
    history = data.get("history", [])

    if not user_message:
        return jsonify({
            "answer": "Please provide a valid question or query.",
            "products": [],
            "sources": [],
            "grounded": False,
            "confidence": 0.0
        }), 400

    # 1. Query Analysis
    query_analysis = query_analyzer.analyze(user_message)

    # 2. Hybrid Retrieval (SQL + pgvector)
    retrieval_result = hybrid_search.hybrid_search(query_analysis)
    candidates = retrieval_result.get("candidates", [])

    # 3. Rerank Candidates
    ranked_candidates = reranker.rerank(candidates, query_analysis)

    # 4. Grounding Evaluation
    is_grounded, fallback_msg, confidence = grounding_guardrail.evaluate_grounding(
        retrieval_result, query_analysis
    )

    if not is_grounded:
        return jsonify({
            "answer": fallback_msg,
            "products": [],
            "sources": [],
            "grounded": False,
            "confidence": float(confidence)
        }), 200

    # 5. LLM Grounded Answer Generation
    answer = generator.generate_response(user_message, ranked_candidates, history)

    # 6. Build Clean Product & Source Payload
    products_payload = []
    sources_payload = []
    seen_sources = set()

    for candidate in ranked_candidates:
        prod = candidate.get("product", {})
        if prod.get("name"):
            products_payload.append({
                "id": prod.get("id"),
                "name": prod.get("name"),
                "brand": prod.get("brand"),
                "price": prod.get("price"),
                "ram": prod.get("ram"),
                "storage": prod.get("storage"),
                "image_path": prod.get("image_path")
            })

        source_url = candidate.get("source_url")
        if source_url and source_url not in seen_sources:
            seen_sources.add(source_url)
            sources_payload.append({
                "source_type": "instagram",
                "source_url": source_url
            })

    return jsonify({
        "answer": answer,
        "products": products_payload,
        "sources": sources_payload,
        "grounded": True,
        "confidence": round(float(confidence), 4)
    }), 200
