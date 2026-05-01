# Phase 4 — Investigator Agent (Stubbed): Requirements

## Goal

Introduce the Investigator agent as a deterministic stub and lock the data contract it will honor in Phase 7. Wire the stub into the pipeline so citations flow Extractor → Investigator → enriched result displayed in the UI. Introduce the Levenshtein fuzzy-match helper (implemented and tested, not yet wired into the stub).

## Scope

### In scope
- `POST /investigate` endpoint: accepts citation list from `/extract`, returns each citation enriched with `found` and `ruling_text`
- Investigator stub: hardcoded list of known Argentine case names; exact match against `case_name` field
- Data contract locked: `{ found: bool, ruling_text: str | null }` — this schema is what the real Investigator (Phase 7) must return
- Realistic Spanish placeholder `ruling_text` for known cases (sufficient for Judge to run semantic comparison in Phase 5)
- `found` badge on CitationCard: green "Encontrado" / red "No encontrado"
- Levenshtein fuzzy-match helper written and unit-tested in `backend/app/utils/fuzzy.py` — not wired into stub yet
- Frontend auto-calls `/investigate` after `/extract` succeeds; new `investigating` spinner state

### Out of scope
- Real database lookups (Phase 7)
- Fuzzy matching in the stub (Phase 7 activates the helper)
- Judge agent (Phase 5)
- Persistence (Phase 6)

## Data Contract (locked for Phase 7)

Each citation returned by `/investigate` extends the Phase 3 citation schema:

```json
{
  "claim": "string",
  "case_name": "string",
  "court": "string",
  "year_tomo_folio": "string | null",
  "found": true,
  "ruling_text": "string — relevant excerpt from the ruling, for semantic comparison"
}
```

Or when not found:

```json
{
  "claim": "string",
  "case_name": "string",
  "court": "string",
  "year_tomo_folio": "string | null",
  "found": false,
  "ruling_text": null
}
```

The real Investigator in Phase 7 must honor this exact schema. The Judge agent in Phase 5 is built against it.

## Decisions

| Decision | Choice | Reason |
|---|---|---|
| Stub known cases | Hardcoded list in code | Simple and sufficient; easy to replace in Phase 7 |
| Endpoint design | Separate `POST /investigate` | Each stage independently testable; clean separation of concerns |
| Fuzzy match | Implemented but not wired | Preserves Phase 7 boundary; still covered by tests |
| Placeholder ruling_text | Realistic Spanish legal excerpt | Gives the Phase 5 Judge enough to run a real semantic comparison during testing |
| UI | Found badge on citation cards | Visible pipeline progress without rebuilding the layout for Phase 5 |
