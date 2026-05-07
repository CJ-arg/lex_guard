"use client";

import { useState } from "react";
import { API_URL, fetchWithTimeout } from "@/lib/api";
import CitationCard, { type Citation } from "./CitationCard";

interface Props {
  filename: string;
  citations: Citation[];
  onReset: () => void;
  readOnly?: boolean;
  sessionMeta?: { user_note?: string | null; created_at?: string };
}

type SaveState =
  | { phase: "idle" }
  | { phase: "noting" }
  | { phase: "saving" }
  | { phase: "saved"; session_id: string }
  | { phase: "error"; message: string };

const BTN_LINK = "text-sm text-blue-400 hover:text-blue-300 transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 rounded";
const BTN_PRIMARY = "text-sm bg-blue-600 hover:bg-blue-500 text-white rounded-lg px-4 py-2 transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-400";
const BTN_GHOST = "text-sm text-zinc-500 hover:text-zinc-300 transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-zinc-500 rounded";
const BTN_SAVE = "self-start text-sm text-zinc-400 hover:text-zinc-200 border border-zinc-700 hover:border-zinc-500 rounded-lg px-4 py-2 transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-zinc-400";

export default function CitationList({ filename, citations, onReset, readOnly, sessionMeta }: Props) {
  const [save, setSave] = useState<SaveState>({ phase: "idle" });
  const [note, setNote] = useState("");

  async function handleSave() {
    setSave({ phase: "saving" });
    try {
      const res = await fetchWithTimeout(`${API_URL}/sessions`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ document_name: filename, user_note: note || null, citations }),
      });
      const data = await res.json();
      if (!res.ok) {
        setSave({ phase: "error", message: data.detail ?? "No se pudo guardar el informe." });
        return;
      }
      setSave({ phase: "saved", session_id: data.session_id });
    } catch (err) {
      setSave({ phase: "error", message: err instanceof Error ? err.message : "No se pudo guardar el informe." });
    }
  }

  const permalink = save.phase === "saved"
    ? `${typeof window !== "undefined" ? window.location.origin : ""}/sessions/${save.session_id}`
    : null;

  return (
    <div className="flex flex-col gap-4 w-full max-w-2xl">
      <div className="flex items-start justify-between gap-4">
        <div className="min-w-0 flex-1">
          <span className="text-zinc-400 text-sm font-mono truncate block">{filename}</span>
          {sessionMeta?.created_at && (
            <span className="text-zinc-600 text-xs">{new Date(sessionMeta.created_at).toLocaleString("es-AR")}</span>
          )}
          {sessionMeta?.user_note && (
            <span className="text-zinc-500 text-xs block">{sessionMeta.user_note}</span>
          )}
          <span className="text-zinc-500 text-xs">
            {citations.length} {citations.length === 1 ? "cita encontrada" : "citas encontradas"}
          </span>
        </div>
        {!readOnly && (
          <button onClick={onReset} className={`${BTN_LINK} shrink-0`}>
            Subir otro documento
          </button>
        )}
      </div>

      <div className="flex flex-col gap-3">
        {citations.map((c, i) => (
          <CitationCard key={i} citation={c} index={i} />
        ))}
      </div>

      {!readOnly && (
        <div className="border-t border-zinc-800 pt-4 flex flex-col gap-3">
          {save.phase === "idle" && (
            <button onClick={() => setSave({ phase: "noting" })} className={BTN_SAVE}>
              Guardar informe
            </button>
          )}

          {save.phase === "noting" && (
            <div className="flex flex-col gap-2">
              <input
                type="text"
                placeholder="Nota opcional (ej. Demanda Empresa Logística)"
                value={note}
                onChange={(e) => setNote(e.target.value)}
                onKeyDown={(e) => { if (e.key === "Enter") handleSave(); }}
                className="bg-zinc-900 border border-zinc-700 rounded-lg px-3 py-2 text-sm text-zinc-200 placeholder-zinc-600 focus:outline-none focus:border-zinc-500 focus-visible:ring-2 focus-visible:ring-blue-500"
              />
              <div className="flex gap-2">
                <button onClick={handleSave} className={BTN_PRIMARY}>
                  Confirmar
                </button>
                <button onClick={() => setSave({ phase: "idle" })} className={BTN_GHOST}>
                  Cancelar
                </button>
              </div>
            </div>
          )}

          {save.phase === "saving" && (
            <p className="text-zinc-500 text-sm">Guardando…</p>
          )}

          {save.phase === "saved" && permalink && (
            <div className="flex flex-col gap-1">
              <p className="text-green-400 text-sm">Informe guardado.</p>
              <div className="flex items-center gap-2 flex-wrap">
                <code className="text-zinc-400 text-xs bg-zinc-900 border border-zinc-700 rounded px-2 py-1 truncate max-w-xs">
                  {permalink}
                </code>
                <button
                  onClick={() => navigator.clipboard.writeText(permalink)}
                  className={`${BTN_LINK} text-xs shrink-0`}
                >
                  Copiar
                </button>
              </div>
            </div>
          )}

          {save.phase === "error" && (
            <div className="flex items-center gap-3 flex-wrap">
              <p className="text-red-400 text-sm">{save.message}</p>
              <button onClick={handleSave} className={BTN_LINK}>
                Reintentar
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
