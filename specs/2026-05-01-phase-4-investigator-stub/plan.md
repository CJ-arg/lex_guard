# Phase 4 — Investigator Agent (Stubbed): Plan

## Group 1 — Backend: Investigator Stub & Fuzzy Helper

1.1 Create `backend/app/utils/fuzzy.py`:
   - `levenshtein_distance(a: str, b: str) -> int` — standard dynamic programming implementation
   - `is_fuzzy_match(a: str, b: str, threshold: int = 3) -> bool` — True if distance ≤ threshold
   - Not wired into the stub yet; activated in Phase 7

1.2 Create `backend/app/utils/__init__.py` (empty, marks utils as package)

1.3 Create `backend/app/services/agent_investigator_stub.py`:
   - Hardcoded `KNOWN_CASES` dict: maps normalized case names to realistic Spanish ruling excerpts (10 representative Argentine cases)
   - `investigate_citations(citations: list[dict]) -> list[dict]`:
     - For each citation, exact-match `case_name.strip().lower()` against `KNOWN_CASES`
     - Found: return citation + `{"found": True, "ruling_text": <excerpt>}`
     - Not found: return citation + `{"found": False, "ruling_text": None}`

1.4 Add `POST /investigate` route to `backend/app/main.py`:
   - Body: `{"citations": [...]}` (Pydantic model)
   - Calls `investigate_citations(citations)`
   - Returns `{"citations": [...]}` with enriched fields
   - Returns HTTP 422 on failure

## Group 2 — Backend: Tests

2.1 Create `backend/tests/test_fuzzy.py`:
   - Test `levenshtein_distance` with exact match (0), single edit (1), transposition, empty strings
   - Test `is_fuzzy_match` at threshold boundaries

2.2 Create `backend/tests/test_investigator_stub.py`:
   - Test that a known case name returns `found: True` and non-null `ruling_text`
   - Test that an unknown case name returns `found: False` and `ruling_text: None`
   - Test that all citation fields are preserved in the output

## Group 3 — Frontend: Found Badge on Citation Cards

3.1 Update `frontend/src/components/CitationCard.tsx`:
   - Add optional props `found?: boolean` and `ruling_text?: string | null`
   - Render green "Encontrado ✓" badge when `found === true`
   - Render red "No encontrado ✗" badge when `found === false`
   - No badge rendered when `found` is undefined (backward compatible)

3.2 Update `frontend/src/components/CitationList.tsx`:
   - Pass `found` and `ruling_text` fields through to each `CitationCard`

## Group 4 — Frontend: Wire /investigate into the Flow

4.1 Add `investigating` state to the state machine in `frontend/src/app/page.tsx`:
   - Holds `filename`, `citations` (unenriched), for display during spinner
   - Transition: `extracting` → `investigating` → `citations` (enriched) or `investigate_error`

4.2 After `/extract` succeeds, automatically call `POST /investigate` with the citation list:
   - Show "Verificando citas…" spinner during the call
   - On success: transition to `citations` state with enriched citation list
   - On API error: transition to `investigate_error` state

4.3 Add `investigate_error` state:
   - Shows inline error message
   - "Try again" re-calls `/investigate` with stored citations (no re-extraction)
   - "Upload another document" resets to idle
