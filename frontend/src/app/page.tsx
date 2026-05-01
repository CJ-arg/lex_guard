"use client";

import { useState } from "react";
import { API_URL } from "@/lib/api";
import UploadZone from "@/components/UploadZone";
import TextPanel from "@/components/TextPanel";

type State =
  | { phase: "idle" }
  | { phase: "loading" }
  | { phase: "success"; filename: string; text: string }
  | { phase: "error"; message: string };

export default function Home() {
  const [state, setState] = useState<State>({ phase: "idle" });

  async function handleFile(file: File) {
    setState({ phase: "loading" });
    const body = new FormData();
    body.append("file", file);
    try {
      const res = await fetch(`${API_URL}/upload`, { method: "POST", body });
      const data = await res.json();
      if (res.ok) {
        setState({ phase: "success", filename: data.filename, text: data.text });
      } else {
        setState({ phase: "error", message: data.detail ?? "Upload failed." });
      }
    } catch {
      setState({ phase: "error", message: "Could not reach the API. Is the backend running?" });
    }
  }

  return (
    <main className="flex min-h-screen flex-col items-center justify-center gap-8 px-4 py-12">
      <h1 className="text-3xl font-bold tracking-tight">LexGuard</h1>

      {state.phase === "idle" && (
        <UploadZone onFile={handleFile} />
      )}

      {state.phase === "loading" && (
        <div className="flex flex-col items-center gap-3 text-zinc-400">
          <svg className="animate-spin h-8 w-8 text-blue-400" viewBox="0 0 24 24" fill="none">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
          </svg>
          <span className="text-sm">Extracting text…</span>
        </div>
      )}

      {state.phase === "success" && (
        <TextPanel
          filename={state.filename}
          text={state.text}
          onReset={() => setState({ phase: "idle" })}
        />
      )}

      {state.phase === "error" && (
        <>
          <p className="text-red-400 text-sm text-center max-w-sm">{state.message}</p>
          <UploadZone onFile={handleFile} />
        </>
      )}
    </main>
  );
}
