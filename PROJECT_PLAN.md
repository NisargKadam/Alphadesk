# AlphaDesk — Project Plan

AlphaDesk is an AI equity research copilot that shows its work: every answer renders
the pipeline that produced it — which route the agent took, which tools it called,
which filing passages it read — before the answer text itself. It is the running
capstone of a 10-session agentic-AI bootcamp for working software engineers who are
new to agents. The repo is built session by session; each session adds exactly one
architectural layer, ends in a working demo, and is captured as one git commit and
one git tag (`session-01` … `session-10`), so the classroom can jump to any session's
exact state.

## Session map

1. **LLM & Agent Foundations** — streaming chat on a raw model call, deliberately
   stateless and tool-less. The two failures this exposes (no memory, unverifiable
   specifics) motivate everything that follows.
2. **LangChain & LangGraph** — the raw call becomes a LangGraph `StateGraph` with
   checkpointed thread state, a router node, and one honest human-in-the-loop
   interrupt.
3. **Retrieval & RAG** — filings ingest → chunking → Chroma → retrieval-augmented,
   cited answers. Session 01's hallucination demo gets fixed on camera.
4. **Tool Use, Function Calling & MCP** — live market data (quotes, price history,
   news) via function calling inside the graph, and the same tools exposed over MCP
   to external agents. *← implemented through here*
5. **Enterprise RAG at Scale** *(ROADMAP)* — the Session 03 pipeline, done properly:
   a chunking-strategy comparison with measurements instead of folklore, hybrid
   (dense + keyword) search, cross-encoder re-ranking replacing the lightweight
   model-call re-rank, and a retrieval evaluation harness so changes are judged by
   numbers, not vibes.
6. **Multi-Agent Systems** *(ROADMAP)* — the single graph becomes a supervisor
   coordinating Market, Filings Analyst, News, and Report Writer sub-agents with
   clean hand-offs. The NodeTrail UI already renders arbitrary paths, so the deeper
   architecture appears in the product for free.
7. **Memory & State** *(ROADMAP)* — the in-process `MemorySaver` checkpointer
   becomes durable storage, a long-term store holds the user's watchlist and
   preferences across threads, and long conversations get summarized instead of
   truncated.
8. **Guardrails & Safety** *(ROADMAP)* — input validation, policy rails that keep
   the desk on the right side of "not investment advice", structured-output checks,
   and a tour of realistic failure modes and how each layer catches them.
9. **Observability & LLMOps** *(ROADMAP)* — tracing across the graph, a token/cost
   panel rendered in the UI itself (the visible pipeline grows a price tag), and
   evaluation runs wired into the workflow.
10. **Full-Stack Deployment** *(ROADMAP)* — Docker Compose for both apps, a polish
    pass, the architecture diagram, and shipping the whole desk.
