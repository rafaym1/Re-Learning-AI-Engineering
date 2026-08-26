from transformers import pipeline

generator = pipeline("text-generation", model="Qwen/Qwen2.5-0.5B-Instruct")


def generate_answer(query: str, context_chunks: list[str]) -> str:
    """Generate an answer to `query`, grounded in `context_chunks`."""
    context = "\n\n".join(context_chunks)
    messages = [
        {"role": "system", "content": "Answer the question using only the provided context."},
        {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {query}"},
    ]
    output = generator(messages, max_new_tokens=200)
    return output[0]["generated_text"][-1]["content"]
