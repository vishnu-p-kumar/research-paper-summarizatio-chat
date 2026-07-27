import { useRef, useState } from "react";
import { api } from "../api.js";

function prettyError(err) {
  return (
    err?.response?.data?.detail ||
    err?.message ||
    "Something went wrong. Please try again."
  );
}

export default function Upload({ onUploaded, onError }) {
  const fileRef = useRef(null);
  const [url, setUrl] = useState("");
  const [busy, setBusy] = useState(false);

  async function uploadPdf(file) {
    const form = new FormData();
    form.append("file", file);
    const res = await api.post("/upload/pdf", form, {
      headers: { "Content-Type": "multipart/form-data" }
    });
    onUploaded?.(res.data);
  }

  async function uploadUrl(paperUrl) {
    const res = await api.post("/upload/url", { url: paperUrl });
    onUploaded?.(res.data);
  }

  return (
    <div className="space-y-4">
      <div>
        <div className="mb-2 text-xs font-semibold uppercase tracking-[0.14em] text-fz-textmuted">
          PDF upload
        </div>
        <div className="rounded-lg border border-dashed border-fz-primary/35 bg-fz-primary/10 p-4">
          <div className="flex flex-col gap-3">
            <div>
              <div className="text-sm font-semibold text-fz-text">
                Choose a research PDF
              </div>
              <div className="mt-1 text-xs leading-5 text-fz-textmuted">
                Best for papers with tables, equations, and formatted sections.
              </div>
            </div>
            <input
              ref={fileRef}
              type="file"
              accept="application/pdf"
              className="w-full text-sm text-fz-textmuted file:mr-3 file:rounded-lg file:border-0 file:bg-fz-primary file:px-3 file:py-2 file:text-sm file:font-bold file:text-black hover:file:brightness-110 disabled:opacity-60"
              disabled={busy}
              onChange={async (e) => {
                const file = e.target.files?.[0];
                if (!file) return;
                setBusy(true);
                try {
                  await uploadPdf(file);
                } catch (err) {
                  onError?.(prettyError(err));
                } finally {
                  setBusy(false);
                  e.target.value = "";
                }
              }}
            />
          </div>
        </div>
      </div>

      <div>
        <div className="mb-2 text-xs font-semibold uppercase tracking-[0.14em] text-fz-textmuted">
          Paper URL
        </div>
        <div className="flex flex-col gap-2 sm:flex-row">
          <input
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="https://arxiv.org/abs/..."
            className="w-full rounded-lg border border-fz-border bg-black/25 px-3 py-2 text-sm text-fz-text placeholder:text-fz-textmuted shadow-sm transition focus:border-fz-primary focus:outline-none focus:ring-2 focus:ring-fz-primary/20"
            disabled={busy}
          />
          <button
            className="rounded-lg bg-fz-primary px-4 py-2 text-sm font-bold text-black shadow-glow transition hover:brightness-110 disabled:cursor-not-allowed disabled:opacity-60"
            disabled={busy || !url.trim()}
            onClick={async () => {
              setBusy(true);
              try {
                await uploadUrl(url.trim());
              } catch (err) {
                onError?.(prettyError(err));
              } finally {
                setBusy(false);
              }
            }}
          >
            {busy ? "Working..." : "Import"}
          </button>
        </div>
        <div className="mt-2 text-xs leading-5 text-fz-textmuted">
          Direct PDF uploads usually extract the cleanest research text.
        </div>
      </div>
    </div>
  );
}

