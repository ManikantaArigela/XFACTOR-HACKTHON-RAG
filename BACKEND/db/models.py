import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Text, Numeric, Boolean, DateTime, ForeignKey, JSON
)
from sqlalchemy.orm import declarative_base, relationship
from config.settings import settings
from db.connection import engine

Base = declarative_base()

# Support PostgreSQL UUID or fallback String UUID for SQLite
is_postgres = engine.dialect.name == "postgresql"

if is_postgres:
    from sqlalchemy.dialects.postgresql import UUID as PG_UUID
    from pgvector.sqlalchemy import Vector
    IdColumnType = PG_UUID(as_uuid=True)
    VectorColumnType = Vector(settings.EMBEDDING_DIMENSION)
else:
    IdColumnType = String(36)
    VectorColumnType = JSON

def generate_uuid_str():
    return str(uuid.uuid4())

class InstagramPost(Base):
    __tablename__ = "instagram_posts"

    id = Column(IdColumnType, primary_key=True, default=generate_uuid_str if not is_postgres else uuid.uuid4)
    instagram_post_id = Column(String(100), unique=True, nullable=False, index=True)
    caption = Column(Text, nullable=False)
    post_url = Column(Text, nullable=True)
    image_path = Column(Text, nullable=True) # Promotional poster flyer image (RAG chat)
    posted_at = Column(DateTime(timezone=True), nullable=True)
    hashtags = Column(JSON, default=list)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    products = relationship("Product", back_populates="source_post")


class Product(Base):
    __tablename__ = "products"

    id = Column(IdColumnType, primary_key=True, default=generate_uuid_str if not is_postgres else uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    brand = Column(String(100), nullable=True, index=True)
    category = Column(String(100), default="smartphone", index=True)
    model = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    price = Column(Numeric(10, 2), nullable=True, index=True)
    ram = Column(String(50), nullable=True)
    storage = Column(String(50), nullable=True)
    specifications = Column(JSON, default=dict)
    availability = Column(Boolean, default=True)
    image_path = Column(Text, nullable=True) # Clean mobile product hardware showcase image
    poster_image_path = Column(Text, nullable=True) # Promotional deal poster flyer image (chat RAG only)
    source_id = Column(IdColumnType, ForeignKey("instagram_posts.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    source_post = relationship("InstagramPost", back_populates="products")


class KnowledgeDocument(Base):
    __tablename__ = "knowledge_documents"

    id = Column(IdColumnType, primary_key=True, default=generate_uuid_str if not is_postgres else uuid.uuid4)
    content = Column(Text, nullable=False)
    source_type = Column(String(50), nullable=False) # 'instagram_post', 'product_catalog', 'store_info'
    source_id = Column(String(100), nullable=False, index=True)
    doc_metadata = Column("metadata", JSON, default=dict)
    embedding = Column(VectorColumnType)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
