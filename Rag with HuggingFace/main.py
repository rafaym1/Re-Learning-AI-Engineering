from pathlib import Path

from rag.chunking import chunk_text
from rag.embeddings import embed_chunks, embed_query
from rag.generation import generate_answer
from rag.vector_store import VectorStore


def main():
    text = Path("data/sample.txt").read_text()
    chunks = chunk_text(text)
    embeddings = embed_chunks(chunks)

    store = VectorStore()
    store.add(chunks, embeddings)

    query = "How do black holes form?"
    query_embedding = embed_query(query)
    results = store.search(query_embedding, top_k=2)

    print(f"Query: {query}\n")
    for i, chunk in enumerate(results, 1):
        print(f"[{i}] {chunk}\n")

    answer = generate_answer(query, results)
    print(f"Answer: {answer}")


if __name__ == "__main__":
    main()
