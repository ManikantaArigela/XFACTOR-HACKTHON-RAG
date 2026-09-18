from datetime import datetime, timezone
from uuid import uuid4

from pgvector.sqlalchemy import Vector

from services.database import db


class ContentEmbedding(db.Model):
    __tablename__ = "content_embeddings"

    id = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid4)
    content_id = db.Column(
        db.UUID(as_uuid=True), db.ForeignKey("contents.id", ondelete="CASCADE"),
        nullable=False, unique=True
    )
    embedding = db.Column(Vector(384), nullable=False)
    source_text = db.Column(db.Text, nullable=False)
    model_name = db.Column(db.String(255), nullable=False)
    created_at = db.Column(
        db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )

    content = db.relationship("Content", back_populates="embedding")
