import CitationCard, { type Citation } from "./CitationCard";

interface Props {
  filename: string;
  citations: Citation[];
  onReset: () => void;
}

export default function CitationList({ filename, citations, onReset }: Props) {
  return (
    <div className="flex flex-col gap-4 w-full max-w-2xl">
      <div className="flex items-center justify-between">
        <div>
          <span className="text-zinc-400 text-sm font-mono truncate block">{filename}</span>
          <span className="text-zinc-500 text-xs">
            {citations.length} {citations.length === 1 ? "cita encontrada" : "citas encontradas"}
          </span>
        </div>
        <button
          onClick={onReset}
          className="text-sm text-blue-400 hover:text-blue-300 transition-colors shrink-0 ml-4"
        >
          Upload another document
        </button>
      </div>

      <div className="flex flex-col gap-3">
        {citations.map((c, i) => (
          <CitationCard key={i} citation={c} index={i} />
        ))}
      </div>
    </div>
  );
}
