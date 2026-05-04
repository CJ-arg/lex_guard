"""Real Investigator: fans out to CSJN, SAIJ, and JUBA in parallel.

Selection rules (WRatio scoring):
  - score < MIN_SCORE  → unverifiable (not confident enough to call it found)
  - score >= MIN_SCORE → found; prefer CSJN (has ruling text) over SAIJ
  - winner written to citation_cache
"""

import asyncio
from typing import Any

from app.services import csjn_adapter, juba_adapter, saij_adapter
from app.services.citation_cache import get_cached, set_cached

MIN_SCORE = 0.80  # WRatio; below this we are not confident it's the same case


def _best_candidate(candidates: list[dict]) -> dict:
    """Prefer candidates with ruling text, then by score."""
    return max(
        candidates,
        key=lambda c: (bool(c.get("ruling_text")), c["match_score"]),
    )


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

    candidates: list[dict[str, Any]] = [
        c
        for r in raw_results
        if isinstance(r, list)
        for c in r
        if c.get("match_score", 0.0) >= MIN_SCORE
    ]

    if not candidates:
        return {**citation, "found": False, "unverifiable": True}

    winner = _best_candidate(candidates)

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


async def investigate_citations(citations: list[dict]) -> list[dict]:
    return list(await asyncio.gather(*[_investigate_one(c) for c in citations]))
