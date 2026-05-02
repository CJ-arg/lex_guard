# Mission

A single fabricated case citation in a legal brief can collapse an argument, expose a firm to sanctions, and permanently damage an attorney's reputation. As AI-assisted drafting becomes standard practice, the risk of hallucinated jurisprudence — rulings that sound authoritative but do not exist — has become a silent threat at the core of litigation work.

LexGuard exists to eliminate that threat before a brief ever reaches the court.

## What We Do

LexGuard is a pre-filing audit platform for law firms. It accepts a draft brief (PDF or DOCX), automatically isolates every jurisprudential citation, and runs each one through a two-stage verification pipeline:

1. 1. **Existence check** — confirms the ruling is registered in the official Argentine jurisprudence repositories LexGuard treats as sources of truth: **SAIJ** (Sistema Argentino de Información Jurídica — Ministerio de Justicia, 900 000+ documents indexing CSJN, federal and provincial jurisprudence), **CSJN Secretaría de Jurisprudencia** (the canonical source for Supreme Court rulings, addressable directly by the citation format `Fallos: TOMO:PÁGINA`), and **JUBA** (Jurisprudencia de Buenos Aires, SCBA + Cámaras de Apelación bonaerenses). Typos and transpositions are handled with fuzzy matching, so good-faith errors surface as corrections rather than false alarms. When none of the sources can confirm or deny a citation (network failure, source down), the verdict degrades to `unverifiable` rather than `danger`.
2. **Semantic integrity check** — compares what the attorney claims the ruling established against what the ruling actually resolved. A real case cited out of context is as dangerous as a fictitious one.

Each citation returns a verdict on a three-level scale, each accompanied by a plain-language justification the attorney can act on immediately:

- **Approved** — the ruling exists and the interpretation is consistent with what it resolved.
- **Warning** — the ruling exists, but the semantic match is uncertain or the ruling addresses a tangential issue. Advisory only: the attorney reviews the justification and decides whether to revise or retain the citation.
- **Danger** — the ruling does not exist in the verified sources, the case metadata is incorrect, or the ruling's content directly contradicts the attorney's claim.

Results are delivered through a web dashboard. Sessions can be saved for audit trail purposes.

## Who We Serve

- **Attorneys and litigators** — the drafters who bear professional responsibility for every citation in a submission. LexGuard is their final checkpoint before a brief leaves the firm.

## Target Audience

- **Litigation-focused law firms** of any size, regardless of their case management system. LexGuard is a standalone tool — no integration required. Firms that file through Lex100 use it as a pre-upload safety layer; firms on other platforms use it just as effectively.
- **Course students** learning spec-driven development with AI coding agents — LexGuard is a realistic, domain-grounded project that demonstrates how to orchestrate multiple specialized agents around a high-stakes real-world problem.

## What Success Looks Like

No brief leaves a firm with a citation that cannot withstand scrutiny. Every hallucination is caught internally, before opposing counsel or a judge finds it first.

A clean LexGuard report is not a formality — it is the last line of defense between a well-constructed argument and a professional liability claim.

## Sources of Truth

LexGuard verifies citations exclusively against **official, public, free** Argentine repositories. The MVP integrates three:

| Source | Operator | Coverage | Citation key |
|---|---|---|---|
| **SAIJ** (saij.gob.ar) | Ministerio de Justicia y Derechos Humanos | National + provincial jurisprudence; 900 000+ documents updated daily | Internal SAIJ ID (`SUA######`, `FA######`) |
| **CSJN Secretaría de Jurisprudencia** (sjconsulta.csjn.gov.ar) | Corte Suprema de Justicia de la Nación | All Court rulings since 1863; full text since 1994 | `Fallos: TOMO:PÁGINA` |
| **JUBA** (juba.scba.gov.ar) | Suprema Corte de Justicia de Buenos Aires | SCBA + provincial Cámaras de Apelación; sumarios since 1984, full text since 1986 | Carátula + nº de causa |

Each verdict carries the source(s) that confirmed (or failed to confirm) the citation, plus a canonical URL the attorney can open to read the original ruling. This traceability is what makes LexGuard's report defensible inside the firm and, if necessary, before a judge.

Sources outside this list (commercial platforms, blogs, AI-generated databases) are explicitly **not** used. Auditability requires that every verdict trace back to a public, official URL.

## A Tool, Not a Substitute

LexGuard is an assistive instrument. It surfaces information, flags inconsistencies, and reduces the margin for error — but it does not practice law.

The professional judgment, the interpretation of doctrine, and the ultimate responsibility for every citation in a filed brief rests exclusively with the attorney. LexGuard supports that judgment; it does not replace it.
