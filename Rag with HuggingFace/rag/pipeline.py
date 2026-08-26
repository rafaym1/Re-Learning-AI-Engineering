from pathlib import Path

from rag.chunking import chunk_text
from rag.embeddings import embed_chunks, embed_query
from rag.generation import generate_answer
from rag.vector_store import VectorStore


class RagPipeline:
    def __init__(self):
        self.store = VectorStore()

    def index(self, path: str) -> None:
        """Chunk and embed a source document, adding it to the vector store. Run once per document."""
        text = Path(path).read_text()
        chunks = chunk_text(text)
        embeddings = embed_chunks(chunks)
        self.store.add(chunks, embeddings)

    def query(self, question: str, top_k: int = 3) -> str:
        """Answer a question using whatever has been indexed so far. Run as often as you like."""
        query_embedding = embed_query(question)
        results = self.store.search(query_embedding, top_k=top_k)
        return generate_answer(question, results)
