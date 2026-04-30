"use client";

import { useEffect, useState } from "react";
import { API_URL } from "@/lib/api";

type Status = "loading" | "connected" | "unreachable";

export default function Home() {
  const [status, setStatus] = useState<Status>("loading");
  const [message, setMessage] = useState("");

  useEffect(() => {
    fetch(`${API_URL}/health`, { signal: AbortSignal.timeout(5000) })
      .then((res) => (res.ok ? res.json() : null))
      .then((data) => {
        if (data) {
          setStatus("connected");
          setMessage(data.status);
        } else {
          setStatus("unreachable");
        }
      })
      .catch(() => setStatus("unreachable"));
  }, []);

  return (
    <main className="flex min-h-screen flex-col items-center justify-center gap-6">
      <h1 className="text-3xl font-bold tracking-tight">LexGuard</h1>
      {status !== "loading" && (
        <div className="flex items-center gap-3 text-base">
          <span className={status === "connected" ? "dot dot-green" : "dot dot-red"} />
          <span>{status === "connected" ? message : "Backend unreachable"}</span>
        </div>
      )}
    </main>
  );
}
