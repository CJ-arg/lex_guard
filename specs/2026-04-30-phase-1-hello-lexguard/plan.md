# Phase 1 — Hello LexGuard: Plan

## Group 1 — Backend: Health Endpoint

1.1 Add `GET /health` route to `backend/app/main.py` returning `{"status": "LexGuard is live"}`
1.2 Smoke-test locally: start uvicorn (`uvicorn app.main:app --reload`) and confirm `curl http://localhost:8000/health` returns the expected JSON
1.3 Confirm `/docs` (FastAPI auto-docs) loads without errors

## Group 2 — Frontend: Environment Wiring

2.1 Copy `frontend/.env.example` to `frontend/.env.local`; set `NEXT_PUBLIC_API_URL=http://localhost:8000`
2.2 Create `frontend/src/lib/api.ts` exporting a typed `API_URL` constant read from `process.env.NEXT_PUBLIC_API_URL`

## Group 3 — Frontend: Status Indicator Page

3.1 Replace the boilerplate content in `frontend/src/app/page.tsx` with a server component that fetches `${API_URL}/health` at request time
3.2 On success: render a green dot + "Backend connected" with the status value from the response
3.3 On fetch error (network failure, non-2xx, timeout): render a red dot + "Backend unreachable"
3.4 Add indicator dot styles to `frontend/src/app/globals.css` (two CSS classes: `.dot-green`, `.dot-red`)

## Group 4 — Deployment Config

4.1 Add `backend/render.yaml` declaring the web service: build command, start command, and `ANTHROPIC_API_KEY` as an env var placeholder
4.2 Set `NEXT_PUBLIC_API_URL` in the Vercel dashboard to the Render service URL (manual step, documented in `backend/.env.example`)
4.3 Set `ANTHROPIC_API_KEY` in the Render dashboard (manual step — never committed to the repo)
4.4 Push branch to GitHub; confirm Vercel and Render both pick up the deployment automatically
