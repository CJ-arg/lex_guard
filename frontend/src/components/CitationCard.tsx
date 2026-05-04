interface Citation {
  claim: string;
  case_name: string;
  court: string;
  year_tomo_folio: string | null;
  found?: boolean;
  ruling_text?: string | null;
  verdict?: "approved" | "warning" | "danger" | "unverifiable";
  justification?: string;
  source?: "CSJN" | "SAIJ" | "JUBA";
  source_url?: string | null;
  match_score?: number | null;
  canonical_caratula?: string | null;
  unverifiable?: boolean;
}

interface Props {
  citation: Citation;
  index: number;
}

const VERDICT_STYLES = {
  approved: "bg-green-900/40 text-green-400 border-green-800",
  warning: "bg-yellow-900/40 text-yellow-400 border-yellow-800",
  danger: "bg-red-900/40 text-red-400 border-red-800",
  unverifiable: "bg-zinc-700/60 text-zinc-400 border-zinc-600",
};

const VERDICT_LABELS = {
  approved: "Aprobado ✓",
  warning: "Advertencia ⚠",
  danger: "Peligro ✗",
  unverifiable: "No verificable",
};

function VerdictBadge({ verdict }: { verdict: NonNullable<Citation["verdict"]> }) {
  return (
    <span className={`text-xs font-medium px-2 py-0.5 rounded-full border ${VERDICT_STYLES[verdict]}`}>
      {VERDICT_LABELS[verdict]}
    </span>
  );
}

function FoundBadge({ found }: { found: boolean }) {
  return found ? (
    <span className="text-xs font-medium px-2 py-0.5 rounded-full bg-green-900/40 text-green-400 border border-green-800">
      Encontrado ✓
    </span>
  ) : (
    <span className="text-xs font-medium px-2 py-0.5 rounded-full bg-red-900/40 text-red-400 border border-red-800">
      No encontrado ✗
    </span>
  );
}

function SourceBadge({ source }: { source: "CSJN" | "SAIJ" | "JUBA" }) {
  return (
    <span className="text-xs font-mono px-2 py-0.5 rounded bg-zinc-700 text-zinc-300">
      {source}
    </span>
  );
}

export default function CitationCard({ citation, index }: Props) {
  return (
    <div className="border border-zinc-700 rounded-xl p-5 flex flex-col gap-3 bg-zinc-900">
      <div className="flex items-center justify-between gap-2 flex-wrap">
        <span className="text-xs font-mono text-zinc-500">#{index + 1}</span>
        <div className="flex items-center gap-2 flex-wrap">
          {citation.source && <SourceBadge source={citation.source} />}
          {citation.verdict !== undefined ? (
            <VerdictBadge verdict={citation.verdict} />
          ) : citation.found !== undefined ? (
            <FoundBadge found={citation.found} />
          ) : null}
        </div>
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

      {citation.justification && (
        <div className="border-t border-zinc-700 pt-3">
          <p className="text-zinc-500 text-xs uppercase tracking-wide mb-1">Justificación</p>
          <p className="text-zinc-300 text-sm leading-relaxed">{citation.justification}</p>
        </div>
      )}
    </div>
  );
}

export type { Citation };
