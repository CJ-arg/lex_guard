import { API_URL } from "@/lib/api";

async function fetchHealth(): Promise<{ status: string } | null> {
  try {
    const res = await fetch(`${API_URL}/health`, { cache: "no-store" });
    if (!res.ok) return null;
    return res.json();
  } catch {
    return null;
  }
}

export default async function Home() {
  const health = await fetchHealth();

  return (
    <main className="flex min-h-screen flex-col items-center justify-center gap-6">
      <h1 className="text-3xl font-bold tracking-tight">LexGuard</h1>
      <div className="flex items-center gap-3 text-base">
        <span className={health ? "dot dot-green" : "dot dot-red"} />
        <span>{health ? health.status : "Backend unreachable"}</span>
      </div>
    </main>
  );
}
