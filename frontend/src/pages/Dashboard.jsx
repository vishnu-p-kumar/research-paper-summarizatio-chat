import { useEffect, useMemo, useState } from "react";
import Upload from "../components/Upload.jsx";
import Summary from "../components/Summary.jsx";
import Chat from "../components/Chat.jsx";

const LS_DOC_ID = "ai_paper_doc_id";
const LS_PREVIEW = "ai_paper_preview";

const workflow = [
  { label: "Upload", detail: "PDF or URL" },
  { label: "Index", detail: "Vector store" },
  { label: "Analyze", detail: "Summary" },
  { label: "Ask", detail: "RAG chat" }
];

const sections = [
  {
    id: "summaries",
    label: "Summaries",
    description: "Generate short, detailed, concept, and equation summaries."
  },
  {
    id: "chat",
    label: "Chat",
    description: "Ask grounded questions from the uploaded paper."
  }
];

export default function Dashboard() {
  const [docId, setDocId] = useState(() => localStorage.getItem(LS_DOC_ID) || "");
  const [preview, setPreview] = useState(() => localStorage.getItem(LS_PREVIEW) || "");
  const [uploadError, setUploadError] = useState("");
  const [activeSection, setActiveSection] = useState("summaries");

  const hasDoc = useMemo(() => Boolean(docId), [docId]);

  useEffect(() => {
    if (docId) localStorage.setItem(LS_DOC_ID, docId);
    else localStorage.removeItem(LS_DOC_ID);
  }, [docId]);

  useEffect(() => {
    if (preview) localStorage.setItem(LS_PREVIEW, preview);
    else localStorage.removeItem(LS_PREVIEW);
  }, [preview]);

  return (
    <div className="flex h-full min-h-0 overflow-hidden">
      <aside className="glass-panel z-20 hidden h-full w-[300px] shrink-0 flex-col border-r border-fz-border lg:flex xl:w-[320px]">
        <div className="flex items-center justify-between border-b border-fz-border bg-black/10 p-4">
          <h2 className="text-xs font-bold uppercase tracking-wider text-fz-textmuted">
            Configuration
          </h2>
          <span className="rounded bg-fz-primary/15 px-2 py-1 text-[9px] font-bold uppercase tracking-wider text-fz-primary">
            Paper Lab
          </span>
        </div>

        <div className="min-h-0 flex-1 space-y-6 overflow-y-auto p-4">
          <section className="space-y-3">
            <div className="flex items-center justify-between">
              <h3 className="text-xs font-bold text-fz-text">Research intake</h3>
              <span className={`h-2 w-2 rounded-full ${hasDoc ? "bg-emerald-400" : "bg-amber-300"}`} />
            </div>
            <div className="glass-card rounded-xl p-4">
              <Upload
                onUploaded={({ doc_id, preview: p }) => {
                  setDocId(doc_id);
                  setPreview(p || "");
                  setUploadError("");
                }}
                onError={(msg) => setUploadError(msg)}
              />
              {uploadError ? (
                <div className="mt-4 rounded-lg border border-red-400/25 bg-red-500/10 p-3 text-xs leading-5 text-red-200">
                  {uploadError}
                </div>
              ) : null}
            </div>
          </section>

          <div className="h-px bg-fz-border" />

          <section className="space-y-3">
            <h3 className="text-xs font-bold text-fz-text">Workspace sections</h3>
            <div className="space-y-2">
              {sections.map((section) => {
                const selected = activeSection === section.id;
                return (
                  <button
                    key={section.id}
                    className={`w-full rounded-xl border p-3 text-left transition ${
                      selected
                        ? "border-fz-primary/45 bg-fz-primary/10 shadow-glow"
                        : "border-fz-border bg-black/20 hover:border-white/20"
                    }`}
                    onClick={() => setActiveSection(section.id)}
                  >
                    <div className={selected ? "text-sm font-black text-fz-primary" : "text-sm font-black text-fz-text"}>
                      {section.label}
                    </div>
                    <div className="mt-1 text-xs leading-5 text-fz-textmuted">
                      {section.description}
                    </div>
                  </button>
                );
              })}
            </div>
          </section>

          <div className="h-px bg-fz-border" />

          <section className="space-y-3">
            <h3 className="text-xs font-bold text-fz-text">Pipeline stages</h3>
            <div className="grid grid-cols-2 gap-2">
              {workflow.map((item, index) => {
                const active = index === 0 || hasDoc;
                return (
                  <div
                    key={item.label}
                    className={`rounded-xl border p-3 transition ${
                      active
                        ? "border-fz-primary/35 bg-fz-primary/10 shadow-glow"
                        : "border-fz-border bg-black/20"
                    }`}
                  >
                    <div className={active ? "text-fz-primary" : "text-fz-textmuted"}>
                      <span className="text-lg font-black">0{index + 1}</span>
                    </div>
                    <div className="mt-2 text-[11px] font-bold text-fz-text">{item.label}</div>
                    <div className="text-[9px] font-medium text-fz-textmuted">{item.detail}</div>
                  </div>
                );
              })}
            </div>
          </section>

        </div>
      </aside>

      <section className="flex min-w-0 flex-1 flex-col overflow-hidden">
        <div className="flex h-14 shrink-0 items-center justify-between border-b border-fz-border bg-black/10 px-4 md:px-6">
          <div>
            <p className="text-[10px] font-bold uppercase tracking-[0.22em] text-fz-primary">
              {activeSection === "summaries" ? "Summaries" : "Chat"}
            </p>
            <h1 className="font-display text-lg font-bold tracking-tight text-fz-text md:text-xl">
              {activeSection === "summaries" ? "Paper summary workspace" : "Paper chat workspace"}
            </h1>
          </div>
          <div className="hidden items-center gap-2 rounded-full border border-fz-border bg-black/20 px-3 py-1 text-[10px] font-mono text-fz-primary sm:flex">
            <span className="h-1.5 w-1.5 animate-ping rounded-full bg-fz-primary" />
            Live RAG Sync
          </div>
        </div>

        <div className="min-h-0 flex-1 overflow-y-auto p-4 md:p-6">
          <div className="mx-auto max-w-6xl">
            <div className="space-y-5">
                  <div className="lg:hidden">
                    <div className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
                      <div className="mb-3 flex items-center justify-between">
                        <div>
                          <p className="text-xs font-bold uppercase tracking-[0.18em] text-sky-600">
                            Step 1
                          </p>
                          <h3 className="mt-1 text-lg font-black text-slate-950">Upload paper</h3>
                        </div>
                        <span className={`rounded-full px-2.5 py-1 text-[10px] font-bold uppercase tracking-wider ${
                          hasDoc ? "bg-emerald-50 text-emerald-700" : "bg-amber-50 text-amber-700"
                        }`}>
                          {hasDoc ? "Ready" : "Needed"}
                        </span>
                      </div>
                      <Upload
                        onUploaded={({ doc_id, preview: p }) => {
                          setDocId(doc_id);
                          setPreview(p || "");
                          setUploadError("");
                        }}
                        onError={(msg) => setUploadError(msg)}
                      />
                      {uploadError ? (
                        <div className="mt-4 rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700">
                          {uploadError}
                        </div>
                      ) : null}
                    </div>
                  </div>
                  <div className="lg:hidden">
                    <div className="grid grid-cols-2 gap-2 rounded-lg border border-slate-200 bg-white p-2 shadow-sm">
                      {sections.map((section) => {
                        const selected = activeSection === section.id;
                        return (
                          <button
                            key={section.id}
                            className={`rounded-lg px-3 py-2 text-sm font-bold transition ${
                              selected
                                ? "bg-slate-950 text-white"
                                : "bg-slate-50 text-slate-600 hover:bg-slate-100"
                            }`}
                            onClick={() => setActiveSection(section.id)}
                          >
                            {section.label}
                          </button>
                        );
                      })}
                    </div>
                  </div>
                  {activeSection === "summaries" ? (
                    <Summary docId={docId} />
                  ) : (
                    <Chat docId={docId} />
                  )}
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
