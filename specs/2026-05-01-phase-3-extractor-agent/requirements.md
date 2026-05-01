# Phase 3 — Extractor Agent: Requirements

## Goal

Wire Claude Haiku as the Extractor agent. Given the plain text extracted in Phase 2, the agent identifies every jurisprudential citation in the brief and returns a structured list. The frontend displays these as citation cards.

## Scope

### In scope
- `POST /extract` backend endpoint: accepts `{"text": "..."}`, returns `{"citations": [...]}`
- Claude Haiku called with a Spanish-language prompt designed for Argentine legal citation formats
- Four fields extracted per citation: `claim`, `case_name`, `court`, `year_tomo_folio`
- Frontend: after a successful upload, automatically calls `/extract` and shows citation cards
- No-citations fallback: if the agent returns an empty list, display the raw extracted text
- Error handling: inline error with a "Try again" button if the API call fails or returns malformed JSON

### Out of scope
- Verification of citations (Phase 4+)
- Semantic judgment of claims (Phase 5)
- Persistence of results (Phase 6)
- Streaming responses (post-MVP)

## Citation Schema

Each citation object returned by the agent:

```json
{
  "claim": "string — what the attorney asserts the ruling established",
  "case_name": "string — caratula, e.g. 'Janon Carlos Alberto S/ SUCESION AB-INTESTATO'",
  "court": "string — tribunal that issued the ruling",
  "year_tomo_folio": "string — publication reference, e.g. '2006, T.88 F.303' (null if not present)"
}
```

## Decisions

| Decision | Choice | Reason |
|---|---|---|
| Prompt language | Spanish | Briefs are in Argentine Spanish; Spanish prompts improve extraction accuracy for legal terminology |
| Response format | Full JSON, no streaming | Simpler implementation; spinner covers the latency adequately for Phase 3 |
| No-citations behavior | Show raw text | Allows attorney to inspect the document even when no citations are found |
| Error behavior | Inline error + retry | Consistent with Phase 2 error pattern; non-destructive |
| Agent model | `claude-haiku-4-5` | Structured extraction task — speed and cost over reasoning depth |
| Endpoint separation | `/upload` and `/extract` are separate | Single responsibility; allows re-running extraction without re-uploading |

## Environment

- `ANTHROPIC_API_KEY` required in backend environment (Render env var for production, `.env` for local)
- Already in `requirements.txt`: `anthropic`
