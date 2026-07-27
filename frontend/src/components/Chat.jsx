import { useEffect, useMemo, useRef, useState } from "react";
import { api } from "../api.js";

const suggestedQuestions = [
  "What is the main contribution?",
  "Explain the method simply.",
  "What are the limitations?"
];

function prettyError(err) {
  return (
    err?.response?.data?.detail ||
    err?.message ||
    "Something went wrong. Please try again."
  );
}

export default function Chat({ docId }) {
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState([]);
  const bottomRef = useRef(null);

  const canChat = useMemo(() => Boolean(docId), [docId]);

  useEffect(() => {
    setMessages([]);
    setError("");
    setBusy(false);
    setInput("");
  }, [docId]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, busy]);

  async function send() {
    const q = input.trim();
    if (!q || !canChat || busy) return;

    setError("");
    setBusy(true);
    setMessages((m) => [...m, { role: "user", content: q }]);
    setInput("");

    try {
      const res = await api.post("/chat", { doc_id: docId, query: q, top_k: 5 });
      setMessages((m) => [
        ...m,
        {
          role: "assistant",
          content: res.data.answer,
          sources: res.data.sources || []
        }
      ]);
    } catch (err) {
      setError(prettyError(err));
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="glass-card rounded-xl p-5">
      <div className="mb-4 flex items-center justify-end">
        <button
          className="rounded-lg border border-fz-border bg-white/5 px-3 py-2 text-xs font-semibold text-fz-textmuted transition hover:border-white/20 hover:text-fz-text disabled:cursor-not-allowed disabled:opacity-50"
          onClick={() => setMessages([])}
          disabled={!messages.length}
        >
          Clear
        </button>
      </div>

      {canChat && !messages.length ? (
        <div className="mb-4 rounded-lg border border-fz-border bg-black/20 p-4">
          <h3 className="text-sm font-bold text-fz-text">Quick questions</h3>
          <div className="mt-3 flex flex-wrap gap-2">
          {suggestedQuestions.map((question) => (
            <button
              key={question}
              className="rounded-full border border-fz-border bg-black/20 px-3 py-1.5 text-xs font-semibold text-fz-textmuted transition hover:border-fz-primary/40 hover:bg-fz-primary/10 hover:text-fz-primary"
              onClick={() => setInput(question)}
              disabled={busy}
            >
              {question}
            </button>
          ))}
          </div>
        </div>
      ) : null}

      <div className="mt-3 h-[430px] overflow-auto rounded-lg border border-fz-border bg-black/25 p-3">
        {messages.length ? (
          <div className="space-y-3">
            {messages.map((m, idx) => (
              <div
                key={idx}
                className={
                  m.role === "user"
                    ? "ml-auto max-w-[85%] rounded-lg rounded-tr-sm bg-fz-primary px-4 py-3 text-sm leading-6 text-black shadow-glow"
                    : "mr-auto max-w-[85%] rounded-lg rounded-tl-sm bg-white/[0.08] px-4 py-3 text-sm leading-6 text-fz-text shadow-sm ring-1 ring-fz-border"
                }
              >
                <div className="whitespace-pre-wrap">{m.content}</div>
                {m.role === "assistant" && Array.isArray(m.sources) && m.sources.length ? (
                  <div className="mt-3 border-t border-white/10 pt-2 text-xs font-medium text-fz-textmuted">
                    Sources:{" "}
                    {m.sources
                      .slice(0, 5)
                      .map((s) => `#${s.chunk_id}`)
                      .join(", ")}
                  </div>
                ) : null}
              </div>
            ))}
            {busy ? (
              <div className="mr-auto max-w-[85%] rounded-lg rounded-tl-sm bg-white/[0.08] px-4 py-3 text-sm text-fz-textmuted shadow-sm ring-1 ring-fz-border">
                Reading retrieved chunks...
              </div>
            ) : null}
          </div>
        ) : (
          <div className="h-full" />
        )}
        <div ref={bottomRef} />
      </div>

      {error ? (
        <div className="mt-3 rounded-lg border border-red-400/25 bg-red-500/10 p-3 text-sm text-red-200">
          {error}
        </div>
      ) : null}

      <div className="mt-3 flex flex-col gap-2 sm:flex-row">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask a question about the paper…"
          className="w-full rounded-lg border border-fz-border bg-black/25 px-3 py-2 text-sm text-fz-text placeholder:text-fz-textmuted shadow-sm transition focus:border-fz-primary focus:outline-none focus:ring-2 focus:ring-fz-primary/20"
          disabled={!canChat || busy}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              send();
            }
          }}
        />
        <button
          className="rounded-lg bg-fz-primary px-5 py-2 text-sm font-bold text-black shadow-glow transition hover:brightness-110 disabled:cursor-not-allowed disabled:opacity-60"
          disabled={!canChat || busy || !input.trim()}
          onClick={send}
        >
          Send
        </button>
      </div>
    </section>
  );
}

