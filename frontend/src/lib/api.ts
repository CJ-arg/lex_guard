export const API_URL =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

const TIMEOUT_MS = 60_000;

export async function fetchWithTimeout(
  url: string,
  options: RequestInit = {}
): Promise<Response> {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), TIMEOUT_MS);
  try {
    return await fetch(url, { ...options, signal: controller.signal });
  } catch (err) {
    if (err instanceof DOMException && err.name === "AbortError") {
      throw new Error("La solicitud tardó demasiado. Verifique su conexión e intente nuevamente.");
    }
    throw new Error("No se pudo conectar con el servidor. Verifique su conexión e intente nuevamente.");
  } finally {
    clearTimeout(timer);
  }
}
