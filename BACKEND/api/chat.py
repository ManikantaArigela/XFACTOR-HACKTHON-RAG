from flask import Blueprint, request, jsonify
from rag import rag_service

chat_bp = Blueprint("chat_bp", __name__)

@chat_bp.route("/api/chat", methods=["POST", "OPTIONS"])
def chat_endpoint():
    if request.method == "OPTIONS":
        return jsonify({"status": "ok"}), 200

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

    # Execute end-to-end local RAG query pipeline (analysis, retrieval, reranking, grounding, generation)
    result = rag_service.answer_query(user_message, history=history)

    return jsonify(result), 200
