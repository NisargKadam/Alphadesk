// useChat — all conversation state in one hook (no state library, on
// purpose): the interesting state lives server-side in the graph
// checkpoint; the client only mirrors the stream into render state.
// Introduced in Session 01.
import { useCallback, useState } from "react";
import { readSSE } from "../lib/stream";

export interface ChatMessage {
  role: "user" | "assistant";
  text: string;
  streaming: boolean;
  error?: string;
}

// Override with VITE_API_BASE if your backend runs on another port.
const API = import.meta.env.VITE_API_BASE ?? "http://localhost:8000";

export function useChat() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [busy, setBusy] = useState(false);

  // Every stream event mutates the last message — the assistant reply
  // currently being streamed.
  const patchLast = (fn: (m: ChatMessage) => ChatMessage) =>
    setMessages((ms) => ms.map((m, i) => (i === ms.length - 1 ? fn(m) : m)));

  const send = useCallback(
    async (text: string) => {
      const message = text.trim();
      if (!message || busy) return;
      setBusy(true);
      setMessages((ms) => [
        ...ms,
        { role: "user", text: message, streaming: false },
        { role: "assistant", text: "", streaming: true },
      ]);
      try {
        await readSSE(`${API}/api/chat`, { message }, (ev) => {
          if (ev.type === "token") {
            patchLast((m) => ({ ...m, text: m.text + ev.text }));
          } else if (ev.type === "error") {
            patchLast((m) => ({
              ...m,
              streaming: false,
              error: `The model call failed: ${ev.message}`,
            }));
          } else if (ev.type === "done") {
            patchLast((m) => ({ ...m, streaming: false }));
          }
        });
      } catch {
        patchLast((m) => ({
          ...m,
          streaming: false,
          error: "Could not reach the backend on port 8000. Start it with `uvicorn app.main:app --reload --port 8000`, then retry.",
        }));
      } finally {
        setBusy(false);
      }
    },
    [busy],
  );

  return { messages, busy, send };
}
