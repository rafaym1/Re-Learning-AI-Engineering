from sentence_transformers import SentenceTransformer
import numpy as np

model = SentenceTransformer("all-MiniLM-L6-v2")


def embed_chunks(chunks: list[str]) -> np.ndarray:
    """Embed a list of text chunks into unit-length vectors."""
    return model.encode(chunks, normalize_embeddings=True)


def embed_query(query: str) -> np.ndarray:
    """Embed a single query string into a unit-length vector."""
    return model.encode(query, normalize_embeddings=True)
