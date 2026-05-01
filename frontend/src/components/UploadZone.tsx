"use client";

import { useRef, useState } from "react";

const MAX_BYTES = 1 * 1024 * 1024; // 1 MB
const ALLOWED = [".pdf", ".docx"];

interface Props {
  onFile: (file: File) => void;
}

function validate(file: File): string | null {
  const ext = "." + file.name.split(".").pop()?.toLowerCase();
  if (!ALLOWED.includes(ext)) return "Only PDF and DOCX files are accepted.";
  if (file.size > MAX_BYTES) return "File exceeds the 1 MB size limit.";
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
        onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
        onDragLeave={() => setDragging(false)}
        onDrop={(e) => {
          e.preventDefault();
          setDragging(false);
          const file = e.dataTransfer.files[0];
          if (file) handle(file);
        }}
        onClick={() => inputRef.current?.click()}
        className={`w-full border-2 border-dashed rounded-xl p-12 flex flex-col items-center gap-3 cursor-pointer transition-colors
          ${dragging ? "border-blue-500 bg-blue-950/20" : "border-zinc-600 hover:border-zinc-400"}`}
      >
        <span className="text-4xl">📄</span>
        <p className="text-zinc-300 text-sm text-center">
          Drag and drop a <strong>PDF</strong> or <strong>DOCX</strong> brief here
        </p>
        <p className="text-zinc-500 text-xs">or click to browse — max 1 MB</p>
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
        <p className="text-red-400 text-sm text-center">{error}</p>
      )}
    </div>
  );
}
