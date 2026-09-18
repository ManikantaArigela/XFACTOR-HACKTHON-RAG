import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Text, Numeric, Boolean, DateTime, ForeignKey, JSON
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base, relationship
from pgvector.sqlalchemy import Vector
from config.settings import settings

Base = declarative_base()

class InstagramPost(Base):
    __tablename__ = "instagram_posts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    instagram_post_id = Column(String(100), unique=True, nullable=False, index=True)
    caption = Column(Text, nullable=False)
    post_url = Column(Text, nullable=True)
    image_path = Column(Text, nullable=True)
    posted_at = Column(DateTime(timezone=True), nullable=True)
    hashtags = Column(JSON, default=list)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    products = relationship("Product", back_populates="source_post")


class Product(Base):
    __tablename__ = "products"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
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
    image_path = Column(Text, nullable=True)
    source_id = Column(UUID(as_uuid=True), ForeignKey("instagram_posts.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    source_post = relationship("InstagramPost", back_populates="products")


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)


class KnowledgeDocument(Base):
    __tablename__ = "knowledge_documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content = Column(Text, nullable=False)
    source_type = Column(String(50), nullable=False)  # 'instagram_post', 'product_catalog', 'store_info'
    source_id = Column(String(100), nullable=False, index=True)
    doc_metadata = Column("metadata", JSON, default=dict)
    embedding = Column(Vector(settings.EMBEDDING_DIMENSION))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
