from datetime import datetime, timezone
from uuid import uuid4

from services.database import db


class Content(db.Model):
    __tablename__ = "contents"

    id = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = db.Column(
        db.UUID(as_uuid=True), db.ForeignKey("users.id", ondelete="CASCADE"), nullable=True
    )
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(100), nullable=False, index=True)
    metadata_json = db.Column(db.JSON, nullable=False, default=dict)
    image_path = db.Column(db.String(500), nullable=True)
    created_at = db.Column(
        db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at = db.Column(
        db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc), nullable=False
    )

    author = db.relationship("User", back_populates="contents")
    embedding = db.relationship(
        "ContentEmbedding", back_populates="content", uselist=False,
        cascade="all, delete-orphan"
    )

    def to_dict(self):
        return {
            "id": str(self.id),
            "user_id": str(self.user_id) if self.user_id else None,
            "title": self.title,
            "description": self.description,
            "category": self.category,
            "metadata": self.metadata_json or {},
            "image_path": self.image_path,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
