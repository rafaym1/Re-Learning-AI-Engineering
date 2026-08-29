## Roadmap: FastAPI → AI Engineer

### ✅ Phase 1 — Backend Fundamentals (To be done in Day 1-3)
Learned FastAPI first, then PostgreSQL. Followed tutorials in order, cross-referenced unfamiliar terms as I progressed.

- [Understanding-focused walkthrough](https://www.youtube.com/watch?v=iWS9ogMPOI0&t=29s)
- [Hands-on build](https://www.youtube.com/watch?v=SR5NYCdzKkc&t=4276s)
- [Basics overview](https://www.youtube.com/watch?v=n2Fluyr3lbc)
- [4-part deep dive](https://www.youtube.com/watch?v=74IWNUja05w)
- [Good guide on chatbot](https://dev.to/vipascal99/building-a-full-stack-ai-chatbot-with-fastapi-backend-and-react-frontend-51ph)

**Project:** [Simple chatbot with Hugging Face](https://github.com/rafaym1/Re-Learning-AI-Engineering/tree/main/simple-chatbot-huggingface) good first project for backend-frontend connection.
**Deploy options:** Backend; Render, Replit, HF Inference, GCP, Railway, RunPod. Frontend; Streamlit, Vercel.

### ✅ Phase 2 — LLM APIs (Day 4-5)
Docs > courses here. [Anthropic docs](https://docs.claude.com) or OpenAI API docs. 
Cover the building with Claude section for now. Talk to any LLM and understand the basic concepts like streaming response, tool/function calling, structured JSON output, retry-on-failure, cost tracking etc.
**Project:** PDF Parser with Anthropic (you can find it in repo) good first mini project to understand the above mentioned concepts.

### ✅ Phase 3 — RAG (Day 6-7)
Understand and build RAG from scratch. I recommend watching [LangChain YouTube playlist](https://www.youtube.com/watch?v=wd7TZ4w1mSw&list=PLfaIDFEXuae2LXbO1_PKyVJiQ23ZztA0x&index=1) ps the notebook included in the tutorial is a gem if you sit with it and read it thoroughly. Also refer to the official documentation. Use pgvector over Pinecone; free, builds on Postgres knowledge.
**Project:** Rag with HuggingFace

### ✅ Phase 4 — Ship Product #1 (Day 7-14)
Develop a scalable and sellable product. The best way to find a project worth learning and investing your full attention is to browse freelance websites. You will find projects with detailed requirements. Pick any relevant to your interest and start building with AI. Do not ask AI to build it for you, ask it to guide you and help you understand each and every step from planning to stack decision and beyond. AI can be a great teacher if used the right way. 
I choose to build a sellable financially intelligent system [Repo here](https://github.com/rafaym1/Re-Learning-AI-Engineering/tree/main/Financial%20Document%20Intelligence)

*Remaining phases suggested by Claude — in progress, adding my own resources as I go.*
### ⬜ Phase 5 — Agentic Workflows (2–3 weeks)
[Anthropic's "Building Effective Agents"](https://www.anthropic.com/research/building-effective-agents) guide.
Build one agent in LangGraph, rebuild same agent with raw loop + tool calls (no framework) — see what the framework hides.

### ⬜ Phase 6 — Ship Product #2 (3–4 weeks)
Full stack (FastAPI + Streamlit/frontend, deployed live). Idea: AI tool for reviewing papers/citations.

### ⬜ Phase 7 — Portfolio + Apply (ongoing)
3–4 line README per project: problem, stack, live link. Apply to "AI Engineer" / "Applied AI Engineer" on LinkedIn + Wellfound
