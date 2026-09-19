from typing import List, Union
from sentence_transformers import SentenceTransformer
from config.settings import settings

class VectorEmbedder:
    """Embedding service using SentenceTransformers for generating document and query vectors."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(VectorEmbedder, cls).__new__(cls)
            print(f"[INFO] Loading SentenceTransformer model '{settings.EMBEDDING_MODEL_NAME}'...")
            cls._instance.model = SentenceTransformer(settings.EMBEDDING_MODEL_NAME)
            dim = getattr(cls._instance.model, "get_embedding_dimension", cls._instance.model.get_sentence_embedding_dimension)()
            print(f"[INFO] Embedding model loaded successfully! Vector Dimension: {dim}")
        return cls._instance

    def embed_text(self, text: str) -> List[float]:
        """Generate embedding vector for a single string query or document."""
        if not text:
            text = " "
        embedding = self.model.encode(text, convert_to_numpy=True, normalize_embeddings=True)
        return embedding.tolist()

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embedding vectors for a batch of strings."""
        if not texts:
            return []
        cleaned_texts = [t if t else " " for t in texts]
        embeddings = self.model.encode(cleaned_texts, convert_to_numpy=True, normalize_embeddings=True, batch_size=16)
        return embeddings.tolist()
