from flask import Blueprint, current_app, g, request
from sqlalchemy.exc import SQLAlchemyError

from models import Content, ContentEmbedding
from services.database import db
from services.embedding import embed_text
from utils.responses import failure, success
from utils.security import optional_user_id
from utils.validation import parse_positive_int, require_json_fields

content_bp = Blueprint("content", __name__)


def _embedding_text(payload):
    return " | ".join([payload["title"], payload["description"], payload["category"]])


@content_bp.post("/content")
@optional_user_id
def create_content():
    payload = require_json_fields(request.get_json(silent=True), "title", "description", "category")
    content = Content(
        user_id=g.user_id,
        title=payload["title"].strip(),
        description=payload["description"].strip(),
        category=payload["category"].strip(),
        metadata_json=payload.get("metadata", {}),
        image_path=payload.get("image_path"),
    )
    try:
        text = _embedding_text(payload)
        vector = embed_text(text)
        content.embedding = ContentEmbedding(
            embedding=vector,
            source_text=text,
            model_name=current_app.config["EMBEDDING_MODEL"],
        )
        db.session.add(content)
        db.session.commit()
    except (RuntimeError, SQLAlchemyError) as error:
        db.session.rollback()
        if isinstance(error, RuntimeError):
            return failure("Unable to generate content embedding", 503)
        return failure("Unable to save content", 503)
    return success(content.to_dict(), "Content created successfully", 201)


@content_bp.get("/content/")
def list_content():
    page = parse_positive_int(request.args.get("page"), 1, 1000000)
    limit = parse_positive_int(request.args.get("limit"), 20, 100)
    query = Content.query.order_by(Content.created_at.desc())
    pagination = query.paginate(page=page, per_page=limit, error_out=False)
    return success({
        "items": [item.to_dict() for item in pagination.items],
        "page": pagination.page,
        "limit": pagination.per_page,
        "total": pagination.total,
        "pages": pagination.pages,
    })


@content_bp.get("/content/<uuid:content_id>")
def get_content(content_id):
    content = db.session.get(Content, content_id)
    if not content:
        return failure("Content not found", 404)
    return success(content.to_dict())
