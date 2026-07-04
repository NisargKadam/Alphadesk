# Session 02 — LangChain & LangGraph

## Learning objectives

- Rebuild the same product on a real agent architecture: a LangGraph `StateGraph` with typed state and conditional edges.
- Explain checkpointed thread state — why the client only holds a `thread_id` while the conversation lives server-side.
- Add a router node with structured output and understand routing as classification, not prompt engineering.
- Implement one honest human-in-the-loop pause with `interrupt()` / `Command(resume=...)` — a graph primitive, not an if-statement.
- Stream from a graph: `messages` (tokens), `custom` (node announcements), `updates` (interrupts).

## Live-coding order

1. Terminal — `uv pip install langchain-openai langgraph`; re-pin `requirements.txt`.
2. `backend/app/graph.py` — `DeskState`: messages with the `add_messages` reducer; explain reducers (append, don't replace).
3. `backend/app/graph.py` — `RouteDecision`, a Pydantic schema: the router must emit a label, not prose.
4. `backend/app/graph.py` — the `router` node with `with_structured_output`; import `SYSTEM_PROMPT` from `llm.py` (the prompt survives the rearchitecture).
5. `backend/app/graph.py` — the `respond` node; note `market`/`filings` land here for now — routing skeleton before capabilities (S03/S04).
6. `backend/app/graph.py` — wire `StateGraph`: nodes, `START` edge, conditional edges, `END`.
7. `backend/app/graph.py` — compile with `InMemorySaver` (old tutorials say `MemorySaver`; renamed in 1.x). In-process, gone on restart — durable in Session 07.
8. `backend/app/main.py` — `thread_id` on `ChatRequest`; `config = {"configurable": {"thread_id": ...}}`.
9. `backend/app/main.py` — `stream_graph()` with `stream_mode=["messages", "custom", "updates"]`; filter tokens to the `respond` node so the router's call doesn't leak.
10. Terminal — restart uvicorn; curl the same message twice with the same `thread_id`; the second answer remembers the first. **State, on the wire, ~40 minutes in.**
11. `backend/app/graph.py` — `announce()` via `get_stream_writer()`; every node reports itself on the custom channel.
12. `backend/app/graph.py` — the `clarify` node: `interrupt()` pauses the graph; the resume value comes back as its return. Warn: the node re-executes from the top on resume.
13. `backend/app/main.py` — `POST /api/chat/resume` with `Command(resume=answer)`.
14. `frontend/src/lib/stream.ts` — add the `node` and `interrupt` event types. The parser doesn't change — only the vocabulary.
15. `frontend/src/hooks/useChat.ts` — `thread_id` per tab via `crypto.randomUUID()`; handle `node` (grow the trail, dedupe consecutive repeats) and `interrupt`.
16. `frontend/src/components/NodeTrail.tsx` — the signature element arrives: chips slide in as the graph runs.
17. `frontend/src/components/ApprovalCard.tsx` — the paused graph's question with an inline reply posting to `/api/chat/resume`.
18. `frontend/src/components/MessageBubble.tsx` + `ChatWindow.tsx` + `App.tsx` — wire trail and card, bump suggestions and the session label; run the demo.

## Demo script

1. **"My name is Priya and I mostly track semiconductor stocks."** — point at the NodeTrail: `router → respond`. The graph is now visible in the product.
2. **"What's my name and what do I track?"** — state, on camera. Same `thread_id`, so the checkpointer replays history into the model. Contrast with Session 01's demo 3.
3. **"What about the other one?"** — routed `unclear`; the ApprovalCard appears with the graph genuinely paused mid-run. Answer it (e.g. "I meant Nvidia") and the same reply continues streaming. Show the terminal: the resume is a second HTTP request against the same thread.

## Where it breaks

- **Every message answers like a stranger.** A new `thread_id` is being generated per *message* (e.g. `crypto.randomUUID()` inside `send()` instead of `useMemo`). One id per conversation, or there is no conversation.
- **The router's structured-output tokens leak into the answer.** With `stream_mode="messages"` every LLM call in every node streams. Filter on `metadata["langgraph_node"] == "respond"`.
- **After answering the ApprovalCard, nothing happens.** The resume request must go through `Command(resume=...)` — posting the answer as a normal `/api/chat` message starts a *new* run at the router instead of resuming the paused `interrupt()`.

## Stretch

> **Budget note:** this session lands ~345 changed application lines against the ~250 target — the interrupt/resume loop and its two components don't compress further without losing the lesson. If class time runs short, the items below and the ApprovalCard polish (entrance motion, autofocus, icon) are the first things to cut and revisit here.

- Persist `thread_id` in `localStorage` so a page reload rejoins the same conversation — then discuss why that's a product decision, not just a technical one.
- Add a "reject" button to the ApprovalCard that resumes with a sentinel the graph maps to "answer with what you have".
- Render the compiled graph with `graph.get_graph().draw_mermaid()` and paste it into the README.
