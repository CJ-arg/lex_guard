"""Real Investigator: fans out to CSJN, SAIJ, and JUBA in parallel.

Disambiguation flow:
  - 0 candidates  → unverifiable
  - 1 candidate, score >= DIRECT_THRESHOLD  → direct return
  - multiple candidates  → Haiku LLM picks the best match
  - winner written to citation_cache
"""

import asyncio
import json
import os
from typing import Any

import anthropic

from app.services import csjn_adapter, juba_adapter, saij_adapter
from app.services.citation_cache import get_cached, set_cached

DIRECT_THRESHOLD = 0.85

_client: anthropic.Anthropic | None = None


def _get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        _client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    return _client


def _disambiguate(case_name: str, candidates: list[dict]) -> dict:
    numbered = "\n".join(
        f"{i + 1}. [{c['source']}] {c['canonical_caratula']} (score={c['match_score']:.2f})"
        for i, c in enumerate(candidates)
    )
    prompt = (
        f"Carátula buscada: {case_name}\n\n"
        f"Candidatos encontrados:\n{numbered}\n\n"
        "Responde ÚNICAMENTE con un JSON: {\"index\": <número del mejor candidato, base 1>}"
    )
    msg = _get_client().messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=64,
        messages=[{"role": "user", "content": prompt}],
    )
    raw = msg.content[0].text.strip()
    try:
        data = json.loads(raw)
        idx = int(data["index"]) - 1
        return candidates[max(0, min(idx, len(candidates) - 1))]
    except Exception:
        return candidates[0]


def _build_result(citation: dict, winner: dict) -> dict:
    return {
        **citation,
        "found": True,
        "ruling_text": winner.get("ruling_text"),
        "source": winner.get("source"),
        "source_url": winner.get("source_url"),
        "match_score": winner.get("match_score", 0.0),
        "canonical_caratula": winner.get("canonical_caratula"),
        "unverifiable": False,
    }


async def _investigate_one(citation: dict) -> dict:
    case_name = citation.get("case_name", "")
    tomo_folio = citation.get("year_tomo_folio") or ""

    cached = get_cached(case_name, tomo_folio)
    if cached:
        return {
            **citation,
            "found": True,
            "ruling_text": cached.get("ruling_text"),
            "source": cached.get("source"),
            "source_url": cached.get("source_url"),
            "match_score": cached.get("match_score", 0.0),
            "canonical_caratula": cached.get("canonical_caratula"),
            "unverifiable": False,
        }

    raw_results = await asyncio.gather(
        csjn_adapter.fetch(citation),
        saij_adapter.fetch(citation),
        juba_adapter.fetch(citation),
        return_exceptions=True,
    )

    candidates: list[dict[str, Any]] = []
    for r in raw_results:
        if isinstance(r, list):
            candidates.extend(r)

    if not candidates:
        return {**citation, "found": False, "unverifiable": True}

    candidates.sort(key=lambda c: c["match_score"], reverse=True)
    best = candidates[0]

    if len(candidates) == 1 or best["match_score"] >= DIRECT_THRESHOLD:
        winner = best
    else:
        winner = _disambiguate(case_name, candidates[:5])

    set_cached(
        case_name,
        tomo_folio,
        source=winner["source"],
        source_url=winner.get("source_url"),
        canonical_caratula=winner.get("canonical_caratula"),
        ruling_text=winner.get("ruling_text"),
        match_score=winner.get("match_score", 0.0),
    )

    return _build_result(citation, winner)


async def _investigate_all(citations: list[dict]) -> list[dict]:
    return list(await asyncio.gather(*[_investigate_one(c) for c in citations]))


def investigate_citations(citations: list[dict]) -> list[dict]:
    return asyncio.run(_investigate_all(citations))
