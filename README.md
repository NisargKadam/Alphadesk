# AlphaDesk

An AI equity research copilot that shows its work — every answer renders the
pipeline that produced it: route → tools → evidence → text.

Built session by session across a 10-session agentic-AI bootcamp. Each session is
one git commit and one tag; `git switch -d session-01` (etc.) jumps to any
session's exact state. See [PROJECT_PLAN.md](PROJECT_PLAN.md) for the full map and
[docs/sessions/](docs/sessions/) for per-session notes.

> Educational project — not investment advice.

## Quickstart

One terminal (Python 3.11+). The UI ships as one final commit at the end of the
course — until then, `curl` is the client.

```bash
cd backend
uv venv .venv && uv pip install -r requirements.txt
# or: python -m venv .venv && .venv/bin/pip install -r requirements.txt
cp .env.example .env       # then put your OpenAI API key in .env
.venv/bin/uvicorn app.main:app --reload --port 8000
```

```bash
curl -N localhost:8000/api/chat -H 'Content-Type: application/json' \
  -d '{"message":"What does Apple sell besides the iPhone?"}'
```

## Streaming protocol

`POST /api/chat` with `{"message": "..."}` returns `text/event-stream`. Every
event is one JSON object on a `data:` line, with a `type` field the client
switches on:

```
data: {"type": "token", "text": "Apple"}\n\n
```

The vocabulary grows one session at a time — a client parses this envelope
once, and later sessions only add event types (the final-commit UI adds one
renderer per type):

| Event   | Since | Payload     | Meaning                                  |
| ------- | ----- | ----------- | ---------------------------------------- |
| `token` | S01   | `text`      | One chunk of assistant text — append it. |
| `done`  | S01   | —           | The reply is complete.                   |
| `error` | S01   | `message`   | Something failed; render it, stop.       |

## Session map

1. **LLM & Agent Foundations** — streaming chat on a raw model call *(you are here)*
2. **LangChain & LangGraph** — StateGraph, thread state, HITL interrupt
3. **Retrieval & RAG** — filings ingest, Chroma retrieval, cited answers
4. **Tool Use, Function Calling & MCP** — live market tools, inside and outside the graph
5. – 10. Roadmap: enterprise RAG, multi-agent, memory, guardrails, observability,
   deployment — see [PROJECT_PLAN.md](PROJECT_PLAN.md).
