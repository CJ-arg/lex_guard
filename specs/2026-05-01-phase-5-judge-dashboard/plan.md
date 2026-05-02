# Phase 5 — Judge Agent & Traffic-Light Dashboard: Plan

## Group 1 — Backend: Judge Agent Service

1.1 Create `backend/app/services/agent_judge.py`:
   - `judge_citations(citations: list[dict]) -> list[dict]`
   - For each citation where `found == False`: immediately assign `verdict: "danger"`, fixed Spanish justification — no API call
   - For each citation where `found == True`: call Claude Haiku with a Spanish prompt
     - System prompt: given `claim` and `ruling_text`, return JSON `{"verdict": "approved"|"warning"|"danger", "justification": "..."}`
     - `approved`: claim is consistent with what the ruling actually resolved
     - `warning`: ruling exists but semantic match is uncertain or tangential
     - `danger`: ruling content contradicts or is unrelated to the attorney's claim
   - Parse response JSON; strip markdown fences if present
   - On malformed response: raise `ValueError`

1.2 Add `POST /judge` route to `backend/app/main.py`:
   - Body: `{"citations": [...]}` (citations from `/investigate`)
   - Calls `judge_citations(citations)`
   - Returns `{"citations": [...]}` with `verdict` and `justification` on each
   - Returns HTTP 422 on failure

## Group 2 — Backend: Tests

2.1 Create `backend/tests/test_judge.py`:
   - Test auto-danger logic: citation with `found: False` gets `verdict: "danger"` without API call
   - Test that `verdict` and `justification` fields are present in output
   - Test empty citations list returns `{"citations": []}`
   - (Integration test for real API call is manual — run locally with live key)

## Group 3 — Frontend: Verdict on Citation Cards

3.1 Update `frontend/src/components/CitationCard.tsx`:
   - Add optional props: `verdict?: "approved" | "warning" | "danger"`, `justification?: string`
   - Replace found badge with verdict pill:
     - `approved` → green pill "Aprobado ✓"
     - `warning` → yellow pill "Advertencia ⚠"
     - `danger` → red pill "Peligro ✗"
   - Falls back to found badge if `verdict` is undefined (backward compatible with Phase 4)
   - Add inline "Justificación" section below the fields when `justification` is present

3.2 No changes needed to `CitationList.tsx` — props pass through automatically

## Group 4 — Frontend: Wire /judge into the Flow

4.1 Add `judging` state to `frontend/src/app/page.tsx`:
   - Holds `filename` and `citations` (post-investigate)
   - Shows "Evaluando citas…" spinner

4.2 After `/investigate` succeeds, automatically call `POST /judge`:
   - Transition: `investigating` → `judging` → `citations` (with verdicts) or `judge_error`

4.3 Add `judge_error` state:
   - Inline error + "Try again" (re-calls `/judge` with stored citations)
   - "Upload another document" resets to idle
