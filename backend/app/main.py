"""AlphaDesk API — one streaming chat endpoint.

The SSE event vocabulary this endpoint emits grows one session at a time
(see README, "Streaming protocol"). Session 01: token / done / error.
"""

from dotenv import load_dotenv

load_dotenv()  # backend/.env — secrets stay out of code and out of git

from fastapi import FastAPI  # noqa: E402
from fastapi.middleware.cors import CORSMiddleware  # noqa: E402
from fastapi.responses import StreamingResponse  # noqa: E402
from pydantic import BaseModel  # noqa: E402

from .llm import stream_reply  # noqa: E402  (imported after the env is loaded)
from .sse import event  # noqa: E402

app = FastAPI(title="AlphaDesk")

# The Vite dev server is a different origin, so the browser preflights our
# POST; without these headers the stream never starts.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str


@app.post("/api/chat")
def chat(req: ChatRequest) -> StreamingResponse:
    # The SSE stream is built by hand — no library — because the wire format
    # *is* the lesson: `data: <json>` + blank line, one event at a time, over
    # a response that stays open while the model generates.
    def stream():
        try:
            for token in stream_reply(req.message):
                yield event("token", text=token)
            yield event("done")
        except Exception as exc:
            # A failure mid-stream must be an event, not a dead socket —
            # the frontend can only render what arrives on the wire.
            yield event("error", message=str(exc))

    return StreamingResponse(stream(), media_type="text/event-stream")
