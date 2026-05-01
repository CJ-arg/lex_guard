# Tech Stack

LexGuard is a split-deployment MVP: a Python/FastAPI backend running the agent pipeline, and a Next.js frontend delivering the audit dashboard. Both layers communicate over a REST API; the browser receives a fully interactive client-side UI backed by server-rendered data.

## Core

| Layer | Choice | Rationale |
|---|---|---|
| Backend language | Python | Natural fit for AI/ML tooling, document parsing libraries, and the Anthropic SDK |
| Backend framework | **FastAPI** | Async-first, automatic OpenAPI docs, type-safe with Pydantic — ideal for an agent orchestration API |
| Frontend language | TypeScript | Type safety end-to-end; catches integration errors between the API contract and the UI at compile time |
| Frontend framework | **Next.js** | React-based, supports server components and API routes; native Vercel deployment |
| AI agents | **Anthropic SDK (Python)** | Powers the three-agent pipeline (Extractor, Investigator, Judge) |
| Database | **Supabase (Postgres)** | Hosted free tier; persists audit sessions and citation verdicts; works across both Render and Vercel |
| Backend hosting | **Render** | Free-tier Python web service; handles long-running agent chains without serverless timeout constraints |
| Frontend hosting | **Vercel** | Native Next.js platform; zero-config deployment on push |

## Agent Model Strategy

The three internal agents have different complexity profiles; model selection reflects that:

| Agent | Model | Rationale |
|---|---|---|
| Extractor | `claude-haiku-4-5` | Structured extraction task — fast and cheap; the output is metadata, not judgment |
| Investigator | `claude-haiku-4-5` | Search and match logic; speed matters here as it runs once per citation |
| Judge | `claude-sonnet-4-6` | Semantic reasoning is the core value of the product — this agent justifies the premium |

## Data

- **Supabase (Postgres)** for all persistent storage: audit sessions, citation results, and verdict justifications
- Schema managed via plain SQL migration files; no ORM for MVP
- Each audit session is stored with its full verdict trail to satisfy the traceability requirement from the spec

## Document Parsing

- **PyMuPDF (`fitz`)** — PDF text extraction; handles scanned layout and multi-column formats
- **python-docx** — DOCX ingestion
- Large documents (100+ pages) are chunked before being passed to the Extractor agent to stay within context limits

## Testing

- **pytest** — backend unit and integration tests for agent logic and API routes
- **Vitest** — frontend component and utility tests; configured in `frontend/vitest.config.ts` with jsdom environment and `@testing-library/react`
- Frontend test setup file lives at `frontend/src/test/setup.ts` (imports `@testing-library/jest-dom` matchers)
- Tests live in a `tests/` directory at each layer
- Run via `pytest` (backend) and `npm test` (frontend, watch mode) or `npm run test:run` (frontend, CI single-pass); both must pass before merge

## Tooling

- `uvicorn` for local FastAPI development
- `ruff` for Python linting and formatting
- `eslint` + `prettier` for TypeScript/Next.js
- `python-dotenv` for local environment variable management

## What We Are Not Using

- No Docker — Render handles the Python environment directly; not needed for MVP
- No ORM — raw SQL via `supabase-py` is sufficient at this scale
- No message queue — agent calls are synchronous in the MVP; async job queue is a post-MVP concern
- No GitHub Pages — static hosting cannot serve the FastAPI backend or dynamic dashboard
