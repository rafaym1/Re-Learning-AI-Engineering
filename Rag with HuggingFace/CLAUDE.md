# rag-tutorial

A hands-on, teaching-oriented build of a Retrieval-Augmented Generation (RAG) pipeline. This is a learning project — code should stay simple and legible over clever or "production-grade," since the point is understanding each piece.

## Stack decisions

- **Package manager:** `uv` (not pip/venv directly). Use `uv add <pkg>` to install deps, `uv run <script>` to execute.
- **Python:** pinned to 3.12 via `.python-version`, deliberately *not* the system default (3.14) — the system's 3.14.3 is too new and ML packages (torch, sentence-transformers) may lack prebuilt wheels for it.
- **Models:** Hugging Face open-source models only, no Anthropic/OpenAI API keys in this pipeline.
  - Embeddings: `sentence-transformers` (e.g. `all-MiniLM-L6-v2`), runs fine on CPU.
  - Generation: a small open instruct model, run on CPU.
- **Hardware constraint:** GPU is an NVIDIA MX130 with only 2GB VRAM — not usable for LLM inference. Everything here targets CPU execution; keep model choices small enough to be usable on CPU.

## Working style

This repo is being built incrementally, one RAG concept at a time (ingest/chunk → embed → vector store → retrieve → generate → pipeline → eval). Don't jump ahead and implement later stages before earlier ones are in place and understood.
