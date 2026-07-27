import { useEffect, useMemo, useState } from "react";
import { api } from "../api.js";

function prettyError(err) {
  return (
    err?.response?.data?.detail ||
    err?.message ||
    "Something went wrong. Please try again."
  );
}

export default function Summary({ docId }) {
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [data, setData] = useState(null);

  const canRun = useMemo(() => Boolean(docId), [docId]);

  useEffect(() => {
    setData(null);
    setError("");
    setBusy(false);
  }, [docId]);

  async function run() {
    setBusy(true);
    setError("");
    try {
      const res = await api.post("/summarize", { doc_id: docId });
      setData(res.data);
    } catch (err) {
      setError(prettyError(err));
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="glass-card rounded-xl p-5">
      <div className="flex justify-end">
        <button
          className="rounded-lg bg-fz-secondary px-4 py-2 text-sm font-bold text-white shadow-glow transition hover:brightness-110 disabled:cursor-not-allowed disabled:opacity-60"
          disabled={!canRun || busy}
          onClick={run}
        >
          {busy ? "Generating..." : "Generate summary"}
        </button>
      </div>

      {error ? (
        <div className="mt-4 rounded-lg border border-red-400/25 bg-red-500/10 p-3 text-sm text-red-200">
          {error}
        </div>
      ) : null}

      {busy ? (
        <div className="mt-4 grid grid-cols-1 gap-3 md:grid-cols-3">
          {["Chunking paper", "Writing brief", "Finding concepts"].map((item) => (
            <div
              key={item}
              className="rounded-lg border border-fz-border bg-black/20 p-4"
            >
              <div className="h-2 w-16 rounded bg-fz-secondary/30" />
              <div className="mt-4 text-sm font-semibold text-fz-text">
                {item}
              </div>
              <div className="mt-2 h-2 w-full animate-pulse rounded bg-white/10" />
            </div>
          ))}
        </div>
      ) : null}

      {data ? (
        <div className="mt-5 grid grid-cols-1 gap-4">
          <div className="rounded-lg border border-fz-border bg-black/20 p-5">
            <div className="mb-2 text-xs font-semibold uppercase tracking-[0.14em] text-fz-textmuted">
              Summary
            </div>
            <div className="whitespace-pre-wrap text-sm leading-6 text-fz-textmuted">
              {data.summary || data.detailed_summary}
            </div>
          </div>

          <div className="rounded-lg border border-fz-border bg-black/20 p-5">
            <div className="mb-3 text-xs font-semibold uppercase tracking-[0.14em] text-fz-textmuted">
              Key concepts
            </div>
            {Array.isArray(data.key_concepts) && data.key_concepts.length ? (
              <div className="flex flex-wrap gap-2">
                {data.key_concepts.map((k, idx) => (
                  <span
                    key={idx}
                    className="rounded-full border border-fz-primary/20 bg-fz-primary/10 px-3 py-1 text-sm font-medium text-fz-primary"
                  >
                    {k}
                  </span>
                ))}
              </div>
            ) : (
              <div className="text-sm text-fz-textmuted">No concepts returned.</div>
            )}
          </div>

          <div className="rounded-lg border border-fz-border bg-black/20 p-5">
            <div className="mb-3 text-xs font-semibold uppercase tracking-[0.14em] text-fz-textmuted">
              Equation explanations
            </div>
            {Array.isArray(data.equations) && data.equations.length ? (
              <div className="space-y-3">
                {data.equations.map((e, idx) => (
                  <div
                    key={idx}
                    className="rounded-lg border border-fz-border bg-black/20 p-4"
                  >
                    <div className="whitespace-pre-wrap rounded-lg bg-black/30 px-3 py-2 font-mono text-xs text-fz-text ring-1 ring-fz-border">
                      {e.equation}
                    </div>
                    <div className="mt-3 whitespace-pre-wrap text-sm leading-6 text-fz-textmuted">
                      {e.explanation}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-sm text-fz-textmuted">
                No equations detected or explained.
              </div>
            )}
          </div>
        </div>
      ) : null}
    </section>
  );
}

