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
9. Terminal — boot uvicorn, then `curl -N localhost:8000/api/chat -H 'Content-Type: application/json' -d '{"message":"hi"}'` and watch raw SSE frames scroll. **First run, ~25 minutes in.**
10. `frontend/` — scaffold Vite + React + TS; install `tailwindcss @tailwindcss/vite motion lucide-react`.
11. `frontend/vite.config.ts` — add the Tailwind v4 plugin; note there is no `tailwind.config.js` in v4.
12. `frontend/src/index.css` — `@theme` design tokens: the locked palette and Inter Tight.
13. `frontend/src/lib/stream.ts` — the fetch-based SSE reader; explain why not `EventSource` (GET-only) and why the buffer (frames split across network chunks).
14. `frontend/src/hooks/useChat.ts` — messages state; every stream event patches the last assistant message.
15. `frontend/src/components/Composer.tsx` — input + send.
16. `frontend/src/components/MessageBubble.tsx` — user bubble vs. editorial assistant text; the streaming caret.
17. `frontend/src/components/ChatWindow.tsx` — scroll region, empty-state suggestion buttons.
18. `frontend/src/App.tsx` — wordmark, session label, disclaimer footer; open the browser and run the demo script.

## Demo script

1. **"What does Apple actually sell besides the iPhone?"** — fluent and genuinely useful; parametric knowledge at its best.
2. **"What was Apple's exact revenue in fiscal 2025?"** — depending on the model's mood it either bluffs a precise-sounding figure or (thanks to the system prompt) admits it can't know. Both make the point: nothing in this architecture can *check* a number. This is the hook for retrieval (Session 03).
3. **"What did I just ask you?"** — it has no idea. Point at the `messages` list in `llm.py`: we send one message, so there is nothing to remember. This is the hook for state (Session 02).

## Where it breaks

- **The browser console says "blocked by CORS policy" and nothing streams.** The CORS middleware is missing or lists the wrong origin. It must allow `http://localhost:5173` — the Vite dev server is a different origin than the API, so the browser preflights the POST.
- **Nothing renders until the whole answer is done.** Someone read the response with `await res.text()` or `res.json()` — both buffer the entire body. You must use `res.body.getReader()` and decode chunks as they arrive.
- **`error` event: `'OPENAI_API_KEY'` / auth failure.** Usually uvicorn was started from the repo root, so `load_dotenv()` never found `backend/.env`. Start it from `backend/`, or check the key was actually pasted into `.env` (not `.env.example`).

## Stretch

- Add a stop button: wire an `AbortController` through `readSSE` and cancel the fetch mid-stream.
- Render assistant text as Markdown (`react-markdown`) without breaking the streaming caret.
- Expose `temperature` in the UI and demo the same prompt at 0.0 vs 1.5 — a first taste of sampling as a product decision.
