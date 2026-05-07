"use client";

import { useRef, useState } from "react";

const MAX_BYTES = 1 * 1024 * 1024; // 1 MB
const ALLOWED = [".pdf", ".docx"];

interface Props {
  onFile: (file: File) => void;
}

function validate(file: File): string | null {
  const ext = "." + file.name.split(".").pop()?.toLowerCase();
  if (!ALLOWED.includes(ext)) return "Solo se aceptan archivos PDF y DOCX.";
  if (file.size > MAX_BYTES) return "El archivo supera el límite de 1 MB.";
  return null;
}

export default function UploadZone({ onFile }: Props) {
  const [dragging, setDragging] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  function handle(file: File) {
    const err = validate(file);
    if (err) { setError(err); return; }
    setError(null);
    onFile(file);
  }

  return (
    <div className="flex flex-col items-center gap-4 w-full max-w-lg">
      <div
        role="button"
        tabIndex={0}
        aria-label="Subir documento PDF o DOCX"
        onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
        onDragLeave={() => setDragging(false)}
        onDrop={(e) => {
          e.preventDefault();
          setDragging(false);
          const file = e.dataTransfer.files[0];
          if (file) handle(file);
        }}
        onClick={() => inputRef.current?.click()}
        onKeyDown={(e) => {
          if (e.key === "Enter" || e.key === " ") {
            e.preventDefault();
            inputRef.current?.click();
          }
        }}
        className={`w-full border-2 border-dashed rounded-xl p-12 flex flex-col items-center gap-3 cursor-pointer transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2 focus-visible:ring-offset-black
          ${dragging ? "border-blue-500 bg-blue-950/20" : "border-zinc-600 hover:border-zinc-400"}`}
      >
        <span className="text-4xl" aria-hidden="true">📄</span>
        <p className="text-zinc-300 text-sm text-center">
          Arrastre un archivo <strong>PDF</strong> o <strong>DOCX</strong> aquí
        </p>
        <p className="text-zinc-500 text-xs">o haga clic para seleccionar — máx. 1 MB</p>
      </div>

      <input
        ref={inputRef}
        type="file"
        accept=".pdf,.docx"
        className="hidden"
        onChange={(e) => {
          const file = e.target.files?.[0];
          if (file) handle(file);
          e.target.value = "";
        }}
      />

      {error && (
        <p role="alert" className="text-red-400 text-sm text-center">{error}</p>
      )}
    </div>
  );
}
