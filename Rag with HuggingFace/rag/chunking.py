def chunk_text(text: str, chunk_size: int = 50, overlap: int = 10) -> list[str]:
    """Split text into word chunks of `chunk_size` words, with `overlap` words shared between consecutive chunks."""
    if overlap >= chunk_size:
        raise ValueError(f"overlap ({overlap}) must be smaller than chunk_size ({chunk_size})")
    words = text.split()
    chunks = []
    start = 0
    while start < len(words):
        end = start + chunk_size
        chunk = " ".join(words[start:end])
        chunks.append(chunk)
        start = start + chunk_size - overlap
    return chunks