import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-only-change-me")
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg://postgres:postgres@localhost:5432/arudhra_services",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH", 10 * 1024 * 1024))
    STORAGE_DIR = str((BASE_DIR / os.getenv("STORAGE_DIR", "storage/images")).resolve())
    ALLOWED_IMAGE_EXTENSIONS = {
        extension.strip().lower()
        for extension in os.getenv(
            "ALLOWED_IMAGE_EXTENSIONS", "jpg,jpeg,png,webp"
        ).split(",")
        if extension.strip()
    }
    EMBEDDING_MODEL = os.getenv(
        "EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"
    )
    EMBEDDING_DIMENSION = int(os.getenv("EMBEDDING_DIMENSION", "384"))
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    RAG_MODEL = os.getenv("RAG_MODEL", "gpt-4o-mini")
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*")
