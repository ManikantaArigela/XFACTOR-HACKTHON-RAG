import sys
import os
from sqlalchemy import text

# Ensure root BACKEND directory is in python path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from config.settings import settings
from db.connection import engine
from db.models import Base

def init_database():
    is_postgres = engine.dialect.name == "postgresql"
    print(f"[INFO] Initializing database using engine: {engine.dialect.name}")

    if is_postgres:
        with engine.connect() as conn:
            print("[INFO] Enabling PostgreSQL extensions ('vector', 'uuid-ossp')...")
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
            conn.execute(text('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";'))
            conn.commit()

    print("[INFO] Creating database tables (instagram_posts, products, knowledge_documents)...")
    Base.metadata.create_all(bind=engine)

    if is_postgres:
        with engine.connect() as conn:
            print("[INFO] Creating HNSW index on knowledge_documents(embedding)...")
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_knowledge_documents_embedding 
                ON knowledge_documents USING hnsw (embedding vector_cosine_ops);
            """))
            conn.commit()

    print("[SUCCESS] Database initialization completed successfully!")

if __name__ == "__main__":
    try:
        init_database()
    except Exception as e:
        print(f"[ERROR] Database initialization failed: {e}")
        sys.exit(1)
