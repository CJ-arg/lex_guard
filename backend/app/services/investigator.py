"""Real Investigator: routes citations to their natural source, then dispatches.

Dispatch flow (per citation):
  1. router.route()  →  primary, secondary?, fallback?
  2. fallback=True   →  asyncio.gather on all three adapters (fan-out)
  3. fallback=False  →  call primary; if no result call secondary; record each
  4. winner = highest-scoring candidate above MIN_SCORE, preferring CSJN (has texto)
  5. winner written to citation_cache
"""

import asyncio
from typing import Any, Literal

from app.services import csjn_adapter, juba_adapter, saij_adapter
from app.services.citation_cache import get_cached, set_cached
from app.services.router import SourceKey, route

MIN_SCORE = 0.80  # WRatio; below this we are not confident it's the same case

_ADAPTERS: dict[SourceKey, Any] = {
    "CSJN": csjn_adapter,
    "SAIJ": saij_adapter,
    "JUBA": juba_adapter,
}


def _best_candidate(candidates: list[dict]) -> dict:
    """Prefer candidates with ruling text, then by score."""
    return max(
        candidates,
        key=lambda c: (bool(c.get("ruling_text")), c["match_score"]),
    )


def _build_result(citation: dict, winner: dict, source_routing: dict) -> dict:
    return {
        **citation,
        "found": True,
        "ruling_text": winner.get("ruling_text"),
        "source": winner.get("source"),
        "source_url": winner.get("source_url"),
        "match_score": winner.get("match_score", 0.0),
        "canonical_caratula": winner.get("canonical_caratula"),
        "unverifiable": False,
        "source_routing": source_routing,
    }


async def _call_adapter(source: SourceKey, citation: dict) -> list[dict]:
    try:
        return await _ADAPTERS[source].fetch(citation) or []
    except Exception:
        return []


def _passing(results: list[dict]) -> list[dict]:
    return [r for r in results if r.get("match_score", 0.0) >= MIN_SCORE]


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
            "source_routing": cached.get("source_routing"),
        }

    decision = route(citation)
    source_routing: dict[str, Any] = {
        "primary_attempted": decision["primary"],
        "primary_result": None,
        "secondary_attempted": None,
        "secondary_result": None,
        "fallback_used": decision["fallback"],
    }

    if decision["fallback"]:
        # Fan-out: all three in parallel
        raw = await asyncio.gather(
            _call_adapter("CSJN", citation),
            _call_adapter("SAIJ", citation),
            _call_adapter("JUBA", citation),
        )
        candidates = _passing([c for bucket in raw for c in bucket])
    else:
        # Sequential: primary first, secondary if needed
        primary_results = await _call_adapter(decision["primary"], citation)
        candidates = _passing(primary_results)

        if candidates:
            source_routing["primary_result"] = "found"
        else:
            source_routing["primary_result"] = "not_found"

            if decision["secondary"]:
                source_routing["secondary_attempted"] = decision["secondary"]
                secondary_results = await _call_adapter(decision["secondary"], citation)
                candidates = _passing(secondary_results)
                source_routing["secondary_result"] = "found" if candidates else "not_found"

    if not candidates:
        return {
            **citation,
            "found": False,
            "unverifiable": True,
            "source_routing": source_routing,
        }

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

    return _build_result(citation, winner, source_routing)


async def investigate_citations(citations: list[dict]) -> list[dict]:
    return list(await asyncio.gather(*[_investigate_one(c) for c in citations]))
