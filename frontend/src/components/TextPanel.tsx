"use client";

interface Props {
  filename: string;
  text: string;
  onReset: () => void;
}

export default function TextPanel({ filename, text, onReset }: Props) {
  return (
    <div className="flex flex-col gap-4 w-full max-w-3xl">
      <div className="flex items-center justify-between">
        <span className="text-zinc-400 text-sm font-mono truncate">{filename}</span>
        <button
          onClick={onReset}
          className="text-sm text-blue-400 hover:text-blue-300 transition-colors shrink-0 ml-4"
        >
          Upload another document
        </button>
      </div>
      <pre className="bg-zinc-900 border border-zinc-700 rounded-xl p-6 text-zinc-200 text-sm leading-relaxed overflow-auto max-h-[70vh] whitespace-pre-wrap break-words font-mono">
        {text}
      </pre>
    </div>
  );
}
