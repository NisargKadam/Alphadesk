# Session 01 — LLM & Agent Foundations

## Learning objectives

- Stream tokens from an LLM over a raw HTTP connection and render them as they arrive.
- Read the SSE wire format (`data: <json>` + blank line) directly — no library between you and the protocol.
- State precisely what a bare model call gives you: fluent parametric knowledge, no memory, no way to verify specifics.
- Plant the two failure hooks the rest of the course resolves: statelessness (fixed in Session 02) and unverifiable claims (fixed in Session 03).

## Live-coding order

1. `backend/` — create the venv and install `fastapi uvicorn[standard] openai python-dotenv`; freeze into `requirements.txt`.
2. `backend/.env` — copy `.env.example`, paste the API key; note `.env` is gitignored, `.env.example` is not.
3. `backend/app/sse.py` — write `event()`; put the SSE frame format on screen: `data: {json}\n\n`.
4. `backend/app/llm.py` — the system prompt: concise, plain-spoken, admits uncertainty, no investment advice.
5. `backend/app/llm.py` — `stream_reply()` with `stream=True`; dwell on the messages list holding *only the incoming message*.
6. `backend/app/main.py` — FastAPI app, `load_dotenv()` before importing `llm`.
7. `backend/app/main.py` — CORS middleware for `http://localhost:5173`; explain the preflight that dies without it.
8. `backend/app/main.py` — `POST /api/chat` returning a hand-built `StreamingResponse`.
9. Terminal — boot uvicorn, then `curl -N localhost:8000/api/chat -H 'Content-Type: application/json' -d '{"message":"hi"}'` and watch raw SSE frames scroll. **First run, ~25 minutes in.** The terminal is the client for the whole course — the UI ships as one final commit, after the backend curriculum.

## Demo script

Run each prompt through the same `curl -N` call — the raw frames scrolling by
*are* the product for now.

1. **"What does Apple actually sell besides the iPhone?"** — fluent and genuinely useful; parametric knowledge at its best.
2. **"What was Apple's exact revenue in fiscal 2025?"** — depending on the model's mood it either bluffs a precise-sounding figure or (thanks to the system prompt) admits it can't know. Both make the point: nothing in this architecture can *check* a number. This is the hook for retrieval (Session 03).
3. **"What did I just ask you?"** — it has no idea. Point at the `messages` list in `llm.py`: we send one message, so there is nothing to remember. This is the hook for state (Session 02).

## Where it breaks

- **Nothing prints until the whole answer is done.** The `-N` flag is missing — curl buffers by default, exactly the way a naive client would. Streaming needs cooperation at every hop; the flag is this session's version of that lesson.
- **`error` event: `'OPENAI_API_KEY'` / auth failure.** Usually uvicorn was started from the repo root, so `load_dotenv()` never found `backend/.env`. Start it from `backend/`, or check the key was actually pasted into `.env` (not `.env.example`).
- **CORS notes stay in `main.py` even with no browser in sight.** Leave the middleware and its why-comment in — the final UI commit is the payoff, and the preflight failure it prevents is documented there.

## Stretch

- Accept a `temperature` field on the request and demo the same prompt at 0.0 vs 1.5 — a first taste of sampling as a product decision.
- Swap Chat Completions for OpenAI's Responses API and diff the stream shapes — the envelope survives because nothing downstream parses provider events, only ours.
