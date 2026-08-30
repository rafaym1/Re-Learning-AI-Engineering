from datetime import date, datetime, timezone

import gradio as gr
import spaces

from fdi.embeddings import embed_query
from fdi.reranker import rerank
from fdi.vector_store import VectorStore
from fdi.verification import verify_numbers_in_context
from llm import generate_answer, verify_claims

INDEX_DIR = "data/vector_index"
DAILY_LIMIT_PER_VISITOR = 8

SAMPLE_QUESTIONS = [
    "What was Planet Fitness's total revenue for fiscal year 2025?",
    "Who are the members of Planet Fitness's board of directors?",
    "What is Planet Fitness's Adjusted EBITDA trend over the last few years?",
]

store = VectorStore.load(INDEX_DIR)

# In-memory per-visitor daily cap. Resets on Space restart -- fine for a demo, no database needed.
# Separate from the Voyage rate limiter: this bounds worst-case Gemini usage from one visitor
# against the model's own daily quota, since Gemini calls aren't otherwise throttled here.
_visitor_usage: dict[str, tuple[date, int]] = {}


def _client_ip(request: gr.Request) -> str:
    forwarded = request.headers.get("x-forwarded-for") if request.headers else None
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def _check_and_record_usage(ip: str) -> bool:
    """Returns True if this visitor is still under today's cap, and records the request if so."""
    today = datetime.now(timezone.utc).date()
    last_date, count = _visitor_usage.get(ip, (today, 0))
    if last_date != today:
        count = 0
    if count >= DAILY_LIMIT_PER_VISITOR:
        return False
    _visitor_usage[ip] = (today, count + 1)
    return True


def _build_context(results: list[dict]) -> str:
    """Join retrieved chunks into one context string, each tagged with the source it came from."""
    parts = [f"[{r['category']} / {r['source_path']}]\n{r['text']}" for r in results]
    return "\n\n".join(parts)


@spaces.GPU
def handle_question(question: str, request: gr.Request):
    # This app never touches a GPU -- every call here is a network request to Voyage/Gemini.
    # The decorator exists only because HF's free tier now requires it to satisfy ZeroGPU's
    # startup check (Gradio Spaces on the free tier run on ZeroGPU with no CPU-only option).
    question = (question or "").strip()
    if not question:
        return "Ask a question about Planet Fitness's filings to get started.", "", ""

    ip = _client_ip(request)
    if not _check_and_record_usage(ip):
        return (
            f"You've reached the demo limit of {DAILY_LIMIT_PER_VISITOR} questions for today "
            "-- thanks for trying it out! Come back tomorrow, or check the static walkthrough "
            "further down the page.",
            "",
            "",
        )

    query_embedding = embed_query(question)
    candidates = store.search(query_embedding, top_k=30)
    results = rerank(question, candidates, top_k=10)
    context = _build_context(results)

    answer = generate_answer(question, context)

    sources = sorted({(r["category"], r["source_path"]) for r in results})
    sources_md = "\n".join(f"- **{category}** · {source_path}" for category, source_path in sources)

    unverified_claims = verify_claims(answer, context)
    unmatched_numbers = verify_numbers_in_context(answer, context)
    if not unverified_claims and not unmatched_numbers:
        verification_md = "✅ Every claim and number in this answer matched the retrieved source text."
    else:
        lines = ["⚠️ Verification flagged the following:"]
        for claim in unverified_claims:
            lines.append(f"- {claim.claim} ({claim.reason})")
        for number in unmatched_numbers:
            lines.append(f"- {number} -- not found in source")
        verification_md = "\n".join(lines)

    return answer, sources_md, verification_md


with gr.Blocks(title="Financial Document Intelligence") as demo:
    gr.Markdown(
        "# Financial Document Intelligence\n"
        "Ask a real question against Planet Fitness's public SEC filings (10-Ks and proxy statements), "
        "used here as a stand-in for a confidential virtual data room. Answers are retrieved and "
        "reranked from the source filings, then verified against them before being shown."
    )

    question_box = gr.Textbox(
        label="Your question",
        placeholder="e.g. What was Planet Fitness's total revenue for fiscal year 2025?",
    )
    submit_btn = gr.Button("Ask", variant="primary")
    gr.Examples(examples=SAMPLE_QUESTIONS, inputs=question_box)

    answer_box = gr.Markdown(label="Answer")
    sources_box = gr.Markdown(label="Cited sources")
    verification_box = gr.Markdown(label="Verification")

    submit_btn.click(
        fn=handle_question,
        inputs=[question_box],
        outputs=[answer_box, sources_box, verification_box],
    )
    question_box.submit(
        fn=handle_question,
        inputs=[question_box],
        outputs=[answer_box, sources_box, verification_box],
    )

if __name__ == "__main__":
    demo.launch()
