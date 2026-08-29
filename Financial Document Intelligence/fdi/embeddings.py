import os
import time

import numpy as np
import voyageai
from dotenv import load_dotenv

load_dotenv()

client = voyageai.Client(api_key=os.environ["VOYAGE_API_KEY"])
MODEL = "voyage-finance-2"

BATCH_SIZE = 10
BATCH_DELAY_SECONDS = 25  # Voyage's free tier caps at 3 requests/minute -- padded above 20s for margin


def _normalize(vectors: np.ndarray) -> np.ndarray:
    """Scale to unit length so VectorStore's plain dot product behaves as cosine similarity."""
    return vectors / np.linalg.norm(vectors, axis=-1, keepdims=True)


def embed_chunks(chunks: list[str]) -> np.ndarray:
    """Embed source-document chunks for indexing, in small rate-limit-friendly batches."""
    all_embeddings = []
    for i in range(0, len(chunks), BATCH_SIZE):
        batch = chunks[i : i + BATCH_SIZE]
        result = client.embed(batch, model=MODEL, input_type="document")
        all_embeddings.extend(result.embeddings)
        time.sleep(BATCH_DELAY_SECONDS)
    return _normalize(np.array(all_embeddings))


def embed_query(query: str) -> np.ndarray:
    """Embed a user question for search. input_type='query' skews the embedding for searching, not being searched."""
    result = client.embed([query], model=MODEL, input_type="query")
    return _normalize(np.array(result.embeddings[0]))
