import os
import sys
from datetime import datetime

# Ensure BACKEND directory is on sys.path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from config.settings import settings
from db.connection import SessionLocal
from db.models import InstagramPost, Product, KnowledgeDocument
from ingestion.loader import InstagramDataLoader
from ingestion.cleaner import TextCleaner
from ingestion.extractor import InformationExtractor
from ingestion.document_builder import RAGDocumentBuilder
from embeddings.embedder import VectorEmbedder

def run_ingestion(raw_file_path: str = None):
    if raw_file_path is None:
        raw_file_path = os.path.join(backend_dir, "data", "raw", "instagram_posts.json")

    print(f"\n=======================================================")
    print(f"  STARTING DATA INGESTION PIPELINE")
    print(f"  Target File: {raw_file_path}")
    print(f"=======================================================\n")

    loader = InstagramDataLoader(raw_file_path)
    cleaner = TextCleaner()
    extractor = InformationExtractor()
    doc_builder = RAGDocumentBuilder()
    embedder = VectorEmbedder()

    raw_posts = loader.load()
    session = SessionLocal()

    ingested_count = 0
    updated_count = 0

    try:
        for raw_post in raw_posts:
            # 1. Clean & Process Post
            processed_post = cleaner.process_post(raw_post)
            post_id_str = processed_post["instagram_post_id"]

            # 2. Check for duplicate Instagram post in DB
            poster_url = processed_post.get("poster_image_url") or processed_post.get("image_url") or processed_post.get("local_image_path")
            db_post = session.query(InstagramPost).filter_by(instagram_post_id=post_id_str).first()
            if not db_post:
                db_post = InstagramPost(
                    instagram_post_id=post_id_str,
                    caption=processed_post["caption"],
                    post_url=processed_post.get("post_url"),
                    image_path=poster_url,
                    posted_at=processed_post.get("posted_at"),
                    hashtags=processed_post.get("hashtags", [])
                )
                session.add(db_post)
                session.flush() # Populate db_post.id
                print(f"[INGEST] Added Instagram post record: '{post_id_str}'")
                ingested_count += 1
            else:
                db_post.caption = processed_post["caption"]
                db_post.post_url = processed_post.get("post_url")
                db_post.image_path = poster_url
                db_post.hashtags = processed_post.get("hashtags", [])
                print(f"[INGEST] Updated existing Instagram post record: '{post_id_str}'")
                updated_count += 1

            # 3. Extract Structured Product Information
            product_data = extractor.extract_product_data(processed_post)

            # Check if product already exists for this source post
            db_product = session.query(Product).filter_by(source_id=db_post.id).first()
            if not db_product:
                db_product = Product(
                    name=product_data["name"],
                    brand=product_data["brand"],
                    category=product_data["category"],
                    model=product_data["model"],
                    description=product_data["description"],
                    price=product_data["price"],
                    ram=product_data["ram"],
                    storage=product_data["storage"],
                    specifications=product_data["specifications"],
                    availability=product_data["availability"],
                    image_path=product_data["image_path"],
                    poster_image_path=product_data.get("poster_image_path") or poster_url,
                    source_id=db_post.id
                )
                session.add(db_product)
                session.flush()
                print(f"[PRODUCT] Created product: '{db_product.name}' (Brand: {db_product.brand}, Price: ₹{db_product.price})")
            else:
                db_product.name = product_data["name"]
                db_product.brand = product_data["brand"]
                db_product.price = product_data["price"]
                db_product.ram = product_data["ram"]
                db_product.storage = product_data["storage"]
                db_product.specifications = product_data["specifications"]
                db_product.image_path = product_data["image_path"]
                db_product.poster_image_path = product_data.get("poster_image_path") or poster_url
                print(f"[PRODUCT] Updated product: '{db_product.name}'")

            # 4. Build RAG Document & Generate Embedding
            rag_doc = doc_builder.build_document(processed_post, product_data)
            embedding_vector = embedder.embed_text(rag_doc["content"])

            db_doc = session.query(KnowledgeDocument).filter_by(
                source_type="instagram_post",
                source_id=post_id_str
            ).first()

            if not db_doc:
                db_doc = KnowledgeDocument(
                    content=rag_doc["content"],
                    source_type=rag_doc["source_type"],
                    source_id=rag_doc["source_id"],
                    doc_metadata=rag_doc["metadata"],
                    embedding=embedding_vector
                )
                session.add(db_doc)
                print(f"[VECTOR] Stored {len(embedding_vector)}-dim embedding vector for doc '{post_id_str}'")
            else:
                db_doc.content = rag_doc["content"]
                db_doc.doc_metadata = rag_doc["metadata"]
                db_doc.embedding = embedding_vector
                db_doc.updated_at = datetime.utcnow()
                print(f"[VECTOR] Updated vector embedding for doc '{post_id_str}'")

        session.commit()
        print(f"\n=======================================================")
        print(f"  INGESTION COMPLETE")
        print(f"  New Posts Ingested : {ingested_count}")
        print(f"  Existing Updated   : {updated_count}")
        print(f"=======================================================\n")

    except Exception as e:
        session.rollback()
        print(f"[ERROR] Data ingestion pipeline failed: {e}")
        raise e
    finally:
        session.close()

if __name__ == "__main__":
    run_ingestion()
