# Phase 5 — Judge Agent & Traffic-Light Dashboard: Requirements

## Goal

Wire Claude Haiku as the Judge agent to complete the first end-to-end demo of LexGuard's core value. Each citation is evaluated for semantic integrity: the Judge compares the attorney's claim against the verified ruling text and returns a traffic-light verdict with a plain-language justification. The found badge is replaced by the verdict pill on each citation card.

## Scope

### In scope
- `POST /judge` endpoint: accepts citations enriched by `/investigate`, returns each citation with `verdict` and `justification`
- Judge agent: calls Claude Haiku with a Spanish prompt to compare `claim` vs `ruling_text`
- Auto-danger rule: citations where `found: false` are immediately assigned `verdict: "danger"` — no API call made
- Verdict scale: `approved` / `warning` / `danger`
- Justification: 2-3 sentences in plain Spanish, actionable for the attorney
- CitationCard: found badge replaced by green/yellow/red verdict pill; justification shown inline
- Frontend: new `judging` state ("Evaluando citas…") wired after `/investigate`

### Out of scope
- Persistence of verdicts (Phase 6)
- Real Investigator (Phase 7)
- Batch processing / streaming

## Data Contract

Each citation returned by `/judge` extends the Phase 4 schema:

```json
{
  "claim": "string",
  "case_name": "string",
  "court": "string",
  "year_tomo_folio": "string | null",
  "found": true,
  "ruling_text": "string",
  "verdict": "approved" | "warning" | "danger",
  "justification": "string — 2-3 sentences in plain Spanish"
}
```

For `found: false` (auto-danger, no Judge call):
```json
{
  ...,
  "found": false,
  "ruling_text": null,
  "verdict": "danger",
  "justification": "El fallo no fue encontrado en las fuentes verificadas. No es posible confirmar su existencia ni la interpretación invocada."
}
```

## Decisions

| Decision | Choice | Reason |
|---|---|---|
| Judge model | `claude-haiku-4-5-20251001` | Cost-effective for MVP testing; can be upgraded to Sonnet post-MVP |
| Not-found behavior | Auto-danger, skip Judge call | Ruling doesn't exist → automatically dangerous; saves API tokens |
| Justification style | 2-3 sentences, plain Spanish | Immediately actionable for the attorney without legal jargon |
| Verdict display | Replace found badge with verdict pill | Single source of truth per card; cleaner UI |
| Justification placement | Inline below citation fields | Always visible; the key output of the product |
| Endpoint | Separate `POST /judge` | Consistent with pipeline pattern; independently testable |
