from flask import Blueprint, request
from sqlalchemy.exc import SQLAlchemyError

from models import Content
from services.database import db
from services.embedding import embed_text
from utils.responses import failure, success
from utils.validation import parse_positive_int

search_bp = Blueprint("search", __name__)


@search_bp.get("/search")
def search_content():
    query = request.args.get("q", "").strip()
    if not query:
        return failure("Query parameter 'q' is required", 400)
    limit = parse_positive_int(request.args.get("limit"), 10, 50)
    try:
        vector = embed_text(query)
        distance = Content.embedding.property.mapper.class_.embedding.cosine_distance(vector)
        records = (
            db.session.query(Content, distance.label("distance"))
            .join(Content.embedding)
            .order_by(distance)
            .limit(limit)
            .all()
        )
    except (RuntimeError, SQLAlchemyError):
        db.session.rollback()
        return failure("Search is temporarily unavailable", 503)
    return success({
        "query": query,
        "results": [
            {**content.to_dict(), "similarity": round(1 - float(distance), 6)}
            for content, distance in records
        ],
    })
