import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, scoped_session
from config.settings import settings

sqlite_fallback_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "arudhra_rag.db")
sqlite_url = f"sqlite:///{sqlite_fallback_path}"

def get_working_engine():
    """Attempt PostgreSQL connection; fallback to SQLite if PostgreSQL service is unavailable."""
    try:
        pg_engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True, pool_size=5, max_overflow=10)
        with pg_engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return pg_engine
    except Exception as e:
        print(f"[DB NOTICE] PostgreSQL not available on {settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}. Using local SQLite fallback database ({sqlite_fallback_path}).")
        return create_engine(sqlite_url, connect_args={"check_same_thread": False})

engine = get_working_engine()
SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def check_db_connection() -> bool:
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        print(f"[DB ERROR] Connection failed: {e}")
        return False
