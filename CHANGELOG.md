# Changelog

## 2026-05-03
- Disable JUBA fetch until WebForms POST is implemented
- Fix: reject low-score adapter results (< 0.50) as unverifiable
- Restore fixes reverted by rebase: async investigator + javascript: href guard
- Fix: degrade to warning instead of crashing when LLM judge fails
- Fix: handle empty ruling_text and empty LLM response in judge

## 2026-05-02
- Phase 6: Supabase persistence — save sessions, permalink, read-only view (#5)

## 2026-05-01
- Add changelog skill and generate initial CHANGELOG.md

## 2026-04-30
- Replan: add Vitest testing setup to frontend
- Mark Phase 1 complete in roadmap
- Fix: switch health check to client component
- Remove vercel.json — rootDirectory is a dashboard setting, not a config file property
- Phase 1: add Render and Vercel deployment config
- Phase 1: health endpoint, status indicator UI, phase spec
- Initial project scaffold
