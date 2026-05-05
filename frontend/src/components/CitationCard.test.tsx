import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import CitationCard from "./CitationCard";

const BASE = {
  claim: "las garantías constitucionales son operativas",
  case_name: "Siri Angel",
  court: "Corte Suprema de Justicia de la Nación",
  year_tomo_folio: "1957",
};

describe("CitationCard — Phase 6 verdicts (regression)", () => {
  it("renders approved pill", () => {
    render(<CitationCard citation={{ ...BASE, verdict: "approved" }} index={0} />);
    expect(screen.getByText("Aprobado ✓")).toBeDefined();
  });

  it("renders warning pill", () => {
    render(<CitationCard citation={{ ...BASE, verdict: "warning" }} index={0} />);
    expect(screen.getByText("Advertencia ⚠")).toBeDefined();
  });

  it("renders danger pill", () => {
    render(<CitationCard citation={{ ...BASE, verdict: "danger" }} index={0} />);
    expect(screen.getByText("Peligro ✗")).toBeDefined();
  });
});

describe("CitationCard — Phase 7 unverifiable", () => {
  it("renders grey No verificable pill when verdict is unverifiable", () => {
    render(
      <CitationCard
        citation={{ ...BASE, verdict: "unverifiable", unverifiable: true, found: false }}
        index={0}
      />
    );
    expect(screen.getByText("No verificable")).toBeDefined();
  });

  it("grey pill has neutral zinc colour class", () => {
    const { container } = render(
      <CitationCard citation={{ ...BASE, verdict: "unverifiable" }} index={0} />
    );
    const pill = container.querySelector("span.text-zinc-400");
    expect(pill).not.toBeNull();
  });
});

describe("CitationCard — source routing trace", () => {
  const SR_PRIMARY = {
    primary_attempted: "CSJN",
    primary_result: "found" as const,
    secondary_attempted: null,
    secondary_result: null,
    fallback_used: false,
  };
  const SR_SECONDARY = {
    primary_attempted: "CSJN",
    primary_result: "not_found" as const,
    secondary_attempted: "SAIJ",
    secondary_result: "found" as const,
    fallback_used: false,
  };
  const SR_FALLBACK = {
    primary_attempted: "CSJN",
    primary_result: null,
    secondary_attempted: null,
    secondary_result: null,
    fallback_used: true,
  };

  it("shows primary found trace", () => {
    render(<CitationCard citation={{ ...BASE, verdict: "approved", source_routing: SR_PRIMARY }} index={0} />);
    expect(screen.getByText("Verificado vía CSJN (primaria)")).toBeDefined();
  });

  it("shows secondary found trace", () => {
    render(<CitationCard citation={{ ...BASE, verdict: "warning", source_routing: SR_SECONDARY }} index={0} />);
    expect(screen.getByText("CSJN sin resultado → confirmado por SAIJ")).toBeDefined();
  });

  it("shows fallback trace", () => {
    render(<CitationCard citation={{ ...BASE, verdict: "approved", source_routing: SR_FALLBACK }} index={0} />);
    expect(screen.getByText("Búsqueda en todas las fuentes")).toBeDefined();
  });

  it("does not render routing line when source_routing is absent", () => {
    render(<CitationCard citation={{ ...BASE, verdict: "approved" }} index={0} />);
    expect(screen.queryByText(/verificado vía/i)).toBeNull();
    expect(screen.queryByText(/búsqueda en todas/i)).toBeNull();
  });
});

describe("CitationCard — source badge", () => {
  it("renders CSJN source badge when source is provided", () => {
    render(<CitationCard citation={{ ...BASE, source: "CSJN", verdict: "approved" }} index={0} />);
    expect(screen.getByText("CSJN")).toBeDefined();
  });

  it("does not render source badge when source is absent", () => {
    render(<CitationCard citation={{ ...BASE, verdict: "approved" }} index={0} />);
    expect(screen.queryByText("CSJN")).toBeNull();
    expect(screen.queryByText("SAIJ")).toBeNull();
    expect(screen.queryByText("JUBA")).toBeNull();
  });
});

