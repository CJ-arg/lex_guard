# Phase 1 — Hello LexGuard: Validation

## Local Validation (required before pushing)

### Backend
- [ ] `uvicorn app.main:app --reload` starts without errors from `backend/`
- [ ] `GET http://localhost:8000/health` returns exactly `{"status": "LexGuard is live"}` with HTTP 200
- [ ] `GET http://localhost:8000/docs` loads the FastAPI auto-generated docs page

### Frontend
- [ ] `npm run dev` starts without errors from `frontend/`
- [ ] Browser at `http://localhost:3000` shows a **green dot** and "Backend connected" when the backend is running
- [ ] Browser at `http://localhost:3000` shows a **red dot** and "Backend unreachable" when the backend is stopped
- [ ] `NEXT_PUBLIC_API_URL` is not hardcoded anywhere in source — it is read exclusively from the env var

## Deployment Validation (required before merging to main)

### Render (backend)
- [ ] Render service builds and deploys from the `backend/` directory without errors
- [ ] `GET https://<render-service>.onrender.com/health` returns `{"status": "LexGuard is live"}` from the public URL

### Vercel (frontend)
- [ ] Vercel build succeeds from the `frontend/` directory
- [ ] Production URL shows the **green dot** indicator connected to the Render backend URL
- [ ] `NEXT_PUBLIC_API_URL` is set to the Render URL in the Vercel environment variables — not to localhost

## Definition of Done

All checkboxes above are ticked. The phase is mergeable to `main` when a developer can open the Vercel production URL in a browser and see "Backend connected" with the response served live from Render.
