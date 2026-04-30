# Phase 1 — Hello LexGuard: Requirements

## Goal

Prove that the split-deployment pipeline works end-to-end before any feature code is written.
A developer running both services locally — or with the backend on Render and the frontend on Vercel — should see a live connection status on screen.

## Scope

### In
- `GET /health` endpoint on the FastAPI backend returning `{"status": "LexGuard is live"}`
- Next.js page that fetches `/health` on load and renders a styled connection indicator
- Green indicator ("Backend connected") on success; red indicator ("Backend unreachable") on fetch failure
- `NEXT_PUBLIC_API_URL` read from `.env.local` (not committed); `.env.example` documents the required key
- Render deployment config for the backend (`render.yaml`)
- Vercel deployment works from the `frontend/` subdirectory with no extra config file needed

### Out
- Authentication of any kind
- Any LexGuard feature (document upload, agents, verdicts)
- Database connection
- Loading states or retry logic (deferred to Phase 8)

## Decisions

| Decision | Choice | Reason |
|---|---|---|
| Frontend display | Styled status indicator (green/red dot) | Gives a concrete, testable UI artifact for Phase 1 |
| Error state | Show "Backend unreachable" in UI | Wiring error states now costs nothing; finding them in Phase 8 costs more |
| Env var strategy | Manual `.env.local` copied from `.env.example` | Standard Next.js convention; keeps localhost config out of git |

## Context

- Backend: FastAPI in `backend/app/main.py`, runs via `uvicorn app.main:app --reload`
- Frontend: Next.js App Router in `frontend/src/app/`, runs via `npm run dev`
- API base URL flows through `NEXT_PUBLIC_API_URL` → used in the fetch call on `page.tsx`
- Render detects `backend/` as the root for the Python service; Vercel detects `frontend/` as the root for Next.js
- See `specs/tech-stack.md` for full stack rationale
