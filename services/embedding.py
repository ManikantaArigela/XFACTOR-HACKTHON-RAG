from functools import lru_cache

from flask import current_app


@lru_cache(maxsize=1)
def _load_model(model_name):
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer(model_name)


def embed_text(text):
    model_name = current_app.config["EMBEDDING_MODEL"]
    try:
        vector = _load_model(model_name).encode(text, normalize_embeddings=True)
    except Exception as error:
        raise RuntimeError("Embedding generation failed") from error
    values = vector.tolist()
    expected_dimension = current_app.config["EMBEDDING_DIMENSION"]
    if len(values) != expected_dimension:
        raise RuntimeError("Embedding dimension does not match database schema")
    return values
