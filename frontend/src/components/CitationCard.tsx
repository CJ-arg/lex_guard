interface Citation {
  claim: string;
  case_name: string;
  court: string;
  year_tomo_folio: string | null;
  found?: boolean;
  ruling_text?: string | null;
}

interface Props {
  citation: Citation;
  index: number;
}

export default function CitationCard({ citation, index }: Props) {
  return (
    <div className="border border-zinc-700 rounded-xl p-5 flex flex-col gap-3 bg-zinc-900">
      <div className="flex items-center justify-between">
        <span className="text-xs font-mono text-zinc-500">#{index + 1}</span>
        {citation.found === true && (
          <span className="text-xs font-medium px-2 py-0.5 rounded-full bg-green-900/40 text-green-400 border border-green-800">
            Encontrado ✓
          </span>
        )}
        {citation.found === false && (
          <span className="text-xs font-medium px-2 py-0.5 rounded-full bg-red-900/40 text-red-400 border border-red-800">
            No encontrado ✗
          </span>
        )}
      </div>

      <p className="text-zinc-100 text-sm leading-relaxed">
        <span className="text-zinc-500 text-xs uppercase tracking-wide block mb-1">Afirmación</span>
        {citation.claim}
      </p>

      <p className="text-zinc-300 text-sm">
        <span className="text-zinc-500 text-xs uppercase tracking-wide block mb-1">Carátula</span>
        {citation.case_name}
      </p>

      <div className="flex flex-wrap gap-4">
        {citation.court && (
          <p className="text-zinc-400 text-xs">
            <span className="text-zinc-500 uppercase tracking-wide block mb-0.5">Tribunal</span>
            {citation.court}
          </p>
        )}
        {citation.year_tomo_folio && (
          <p className="text-zinc-400 text-xs font-mono">
            <span className="text-zinc-500 uppercase tracking-wide font-sans block mb-0.5">Referencia</span>
            {citation.year_tomo_folio}
          </p>
        )}
      </div>
    </div>
  );
}

export type { Citation };
