# AlphaDesk

An AI equity research copilot that shows its work — every answer renders the
pipeline that produced it: route → tools → evidence → text.

Built session by session across a 10-session agentic-AI bootcamp. Each session is
one git commit and one tag; `git switch -d session-01` (etc.) jumps to any
session's exact state. See [PROJECT_PLAN.md](PROJECT_PLAN.md) for the full map and
[docs/sessions/](docs/sessions/) for per-session notes.

> Educational project — not investment advice.

## Quickstart

Two terminals.

**Terminal 1 — backend** (Python 3.11+)

```bash
cd backend
uv venv .venv && uv pip install -r requirements.txt
# or: python -m venv .venv && .venv/bin/pip install -r requirements.txt
cp .env.example .env       # then put your OpenAI API key in .env
.venv/bin/uvicorn app.main:app --reload --port 8000
```

**Terminal 2 — frontend**

```bash
cd frontend
npm install
npm run dev                # http://localhost:5173
```

## Streaming protocol

`POST /api/chat` with `{"message": "..."}` returns `text/event-stream`. Every
event is one JSON object on a `data:` line, with a `type` field the frontend
switches on:

```
data: {"type": "token", "text": "Apple"}\n\n
```

The vocabulary grows one session at a time — the frontend parses this envelope
once (in `src/lib/stream.ts`) and later sessions only add renderers:

| Event       | Since | Payload    | Meaning                                          |
| ----------- | ----- | ---------- | ------------------------------------------------ |
| `token`     | S01   | `text`     | One chunk of assistant text — append it.         |
| `done`      | S01   | —          | The stream is complete.                          |
| `error`     | S01   | `message`  | Something failed; render it, stop.               |
| `node`      | S02   | `name`     | A graph node started — grow the NodeTrail.       |
| `interrupt` | S02   | `question` | The graph paused for a human answer (see below). |

Since Session 02 every request also carries a client-generated `thread_id` —
the conversation state lives server-side in the graph checkpointer, keyed by
that id. When an `interrupt` event arrives, the graph is paused;
`POST /api/chat/resume` with `{"thread_id": "...", "answer": "..."}` resumes
it and returns a fresh SSE stream that continues the same reply.

## Session map

1. **LLM & Agent Foundations** — streaming chat on a raw model call
2. **LangChain & LangGraph** — StateGraph, thread state, HITL interrupt *(you are here)*
3. **Retrieval & RAG** — filings ingest, Chroma retrieval, cited answers
4. **Tool Use, Function Calling & MCP** — live market tools, inside and outside the graph
5. – 10. Roadmap: enterprise RAG, multi-agent, memory, guardrails, observability,
   deployment — see [PROJECT_PLAN.md](PROJECT_PLAN.md).
