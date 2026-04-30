# Mission

A single fabricated case citation in a legal brief can collapse an argument, expose a firm to sanctions, and permanently damage an attorney's reputation. As AI-assisted drafting becomes standard practice, the risk of hallucinated jurisprudence — rulings that sound authoritative but do not exist — has become a silent threat at the core of litigation work.

LexGuard exists to eliminate that threat before a brief ever reaches the court.

## What We Do

LexGuard is a pre-filing audit platform for law firms. It accepts a draft brief (PDF or DOCX), automatically isolates every jurisprudential citation, and runs each one through a two-stage verification pipeline:

1. **Existence check** — confirms the ruling is registered in official repositories (CSJN, Federal Appellate Courts / Cámaras Federales, Provincial Supreme Courts, InfoLeg, SAIJ). Typos and transpositions are handled with fuzzy matching, so good-faith errors surface as corrections rather than false alarms.
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

## A Tool, Not a Substitute

LexGuard is an assistive instrument. It surfaces information, flags inconsistencies, and reduces the margin for error — but it does not practice law.

The professional judgment, the interpretation of doctrine, and the ultimate responsibility for every citation in a filed brief rests exclusively with the attorney. LexGuard supports that judgment; it does not replace it.
