"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { API_URL, fetchWithTimeout } from "@/lib/api";
import CitationList from "@/components/CitationList";
import { type Citation } from "@/components/CitationCard";

interface Session {
  id: string;
  document_name: string;
  user_note: string | null;
  created_at: string;
  citations: Citation[];
}

export default function SessionPage() {
  const { id } = useParams<{ id: string }>();
  const [session, setSession] = useState<Session | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchWithTimeout(`${API_URL}/sessions/${id}`)
      .then((res) => {
        if (res.status === 404) throw new Error("Informe no encontrado.");
        if (!res.ok) throw new Error("Error al cargar el informe.");
        return res.json();
      })
      .then(setSession)
      .catch((e: unknown) => setError(e instanceof Error ? e.message : "Error al cargar el informe."));
  }, [id]);

  return (
    <main className="flex min-h-screen flex-col items-center justify-center gap-8 px-4 py-12">
      <h1 className="text-3xl font-bold tracking-tight">LexGuard</h1>

      {!session && !error && (
        <p className="text-zinc-500 text-sm">Cargando informe…</p>
      )}

      {error && (
        <p className="text-red-400 text-sm">{error}</p>
      )}

      {session && (
        <CitationList
          filename={session.document_name}
          citations={session.citations}
          onReset={() => {}}
          readOnly
          sessionMeta={{ user_note: session.user_note, created_at: session.created_at }}
        />
      )}
    </main>
  );
}
