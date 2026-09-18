from flask import Blueprint, request
from sqlalchemy.exc import SQLAlchemyError

from models import Content
from services.database import db
from services.embedding import embed_text
from services.rag import generate_answer
from utils.responses import failure, success
from utils.validation import parse_positive_int

chat_bp = Blueprint("chat", __name__)


@chat_bp.post("/chat")
def chat():
    payload = request.get_json(silent=True) or {}
    query = str(payload.get("query", "")).strip()
    if not query:
        return failure("Field 'query' is required", 400)
    limit = parse_positive_int(payload.get("limit"), 5, 20)
    try:
        vector = embed_text(query)
        distance = Content.embedding.property.mapper.class_.embedding.cosine_distance(vector)
        rows = (
            db.session.query(Content, distance.label("distance"))
            .join(Content.embedding)
            .order_by(distance)
            .limit(limit)
            .all()
        )
        answer = generate_answer(query, [content for content, _distance in rows])
    except (RuntimeError, SQLAlchemyError):
        db.session.rollback()
        return failure("Chat is temporarily unavailable", 503)
    return success({
        "query": query,
        "answer": answer,
        "sources": [content.to_dict() for content, _distance in rows],
    })
