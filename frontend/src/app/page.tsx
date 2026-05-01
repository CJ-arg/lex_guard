"use client";

import { useState } from "react";
import { API_URL } from "@/lib/api";
import UploadZone from "@/components/UploadZone";
import TextPanel from "@/components/TextPanel";
import CitationList from "@/components/CitationList";
import { type Citation } from "@/components/CitationCard";

type State =
  | { phase: "idle" }
  | { phase: "loading" }
  | { phase: "extracting"; filename: string; text: string }
  | { phase: "citations"; filename: string; citations: Citation[] }
  | { phase: "no_citations"; filename: string; text: string }
  | { phase: "upload_error"; message: string }
  | { phase: "extract_error"; message: string; filename: string; text: string };

function Spinner({ label }: { label: string }) {
  return (
    <div className="flex flex-col items-center gap-3 text-zinc-400">
      <svg className="animate-spin h-8 w-8 text-blue-400" viewBox="0 0 24 24" fill="none">
        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
      </svg>
      <span className="text-sm">{label}</span>
    </div>
  );
}

export default function Home() {
  const [state, setState] = useState<State>({ phase: "idle" });

  async function runExtract(filename: string, text: string) {
    setState({ phase: "extracting", filename, text });
    try {
      const res = await fetch(`${API_URL}/extract`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text }),
      });
      const data = await res.json();
      if (!res.ok) {
        setState({ phase: "extract_error", message: data.detail ?? "Extraction failed.", filename, text });
        return;
      }
      const citations: Citation[] = data.citations;
      if (citations.length === 0) {
        setState({ phase: "no_citations", filename, text });
      } else {
        setState({ phase: "citations", filename, citations });
      }
    } catch {
      setState({ phase: "extract_error", message: "Could not reach the API. Is the backend running?", filename, text });
    }
  }

  async function handleFile(file: File) {
    setState({ phase: "loading" });
    const body = new FormData();
    body.append("file", file);
    try {
      const res = await fetch(`${API_URL}/upload`, { method: "POST", body });
      const data = await res.json();
      if (!res.ok) {
        setState({ phase: "upload_error", message: data.detail ?? "Upload failed." });
        return;
      }
      await runExtract(data.filename, data.text);
    } catch {
      setState({ phase: "upload_error", message: "Could not reach the API. Is the backend running?" });
    }
  }

  function reset() {
    setState({ phase: "idle" });
  }

  return (
    <main className="flex min-h-screen flex-col items-center justify-center gap-8 px-4 py-12">
      <h1 className="text-3xl font-bold tracking-tight">LexGuard</h1>

      {state.phase === "idle" && <UploadZone onFile={handleFile} />}

      {state.phase === "loading" && <Spinner label="Subiendo documento…" />}

      {state.phase === "extracting" && <Spinner label="Extrayendo citas…" />}

      {state.phase === "citations" && (
        <CitationList
          filename={state.filename}
          citations={state.citations}
          onReset={reset}
        />
      )}

      {state.phase === "no_citations" && (
        <TextPanel
          filename={state.filename}
          text={state.text}
          onReset={reset}
        />
      )}

      {state.phase === "upload_error" && (
        <>
          <p className="text-red-400 text-sm text-center max-w-sm">{state.message}</p>
          <UploadZone onFile={handleFile} />
        </>
      )}

      {state.phase === "extract_error" && (
        <div className="flex flex-col items-center gap-4">
          <p className="text-red-400 text-sm text-center max-w-sm">{state.message}</p>
          <div className="flex gap-3">
            <button
              onClick={() => runExtract(state.filename, state.text)}
              className="text-sm text-blue-400 hover:text-blue-300 transition-colors"
            >
              Try again
            </button>
            <span className="text-zinc-600">·</span>
            <button
              onClick={reset}
              className="text-sm text-zinc-400 hover:text-zinc-300 transition-colors"
            >
              Upload another document
            </button>
          </div>
        </div>
      )}
    </main>
  );
}
