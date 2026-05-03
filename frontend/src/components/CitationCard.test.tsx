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

describe("CitationCard — canonical caratula correction", () => {
  it("shows correction suggestion when canonical differs from case_name", () => {
    render(
      <CitationCard
        citation={{
          ...BASE,
          case_name: "Siri Angel",
          canonical_caratula: "Siri, Ángel s/ interpone recurso de hábeas corpus",
          verdict: "approved",
        }}
        index={0}
      />
    );
    expect(screen.getByText("Carátula canónica sugerida")).toBeDefined();
    expect(screen.getByText("Siri, Ángel s/ interpone recurso de hábeas corpus")).toBeDefined();
  });

  it("hides correction when canonical matches case_name", () => {
    render(
      <CitationCard
        citation={{
          ...BASE,
          canonical_caratula: "Siri Angel",
          verdict: "approved",
        }}
        index={0}
      />
    );
    expect(screen.queryByText("Carátula canónica sugerida")).toBeNull();
  });

  it("hides correction when canonical_caratula is absent", () => {
    render(<CitationCard citation={{ ...BASE, verdict: "approved" }} index={0} />);
    expect(screen.queryByText("Carátula canónica sugerida")).toBeNull();
  });
});

describe("CitationCard — source URL link", () => {
  it("renders link when source_url is present", () => {
    render(
      <CitationCard
        citation={{
          ...BASE,
          verdict: "approved",
          source_url: "https://sjconsulta.csjn.gov.ar/fallos/1",
        }}
        index={0}
      />
    );
    const link = screen.getByRole("link", { name: /ver fallo original/i });
    expect(link).toBeDefined();
    expect(link.getAttribute("href")).toBe("https://sjconsulta.csjn.gov.ar/fallos/1");
  });

  it("does not render link when source_url is absent", () => {
    render(<CitationCard citation={{ ...BASE, verdict: "approved" }} index={0} />);
    expect(screen.queryByRole("link")).toBeNull();
  });
});
