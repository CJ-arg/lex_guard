"""SAIJ (saij.gob.ar) adapter.

Uses the /busqueda JSON API (discovered from query-object.js).
Response: searchResults.documentResultList[].documentAbstract (JSON)
  -> document.content.{actor, sobre, tribunal, fecha}

SAIJ confirms case existence only — direct document URLs return 500.
source_url points to the SAIJ search page for the carátula.
"""

import json
import re
import urllib.parse
from typing import TypedDict

import httpx
from rapidfuzz import fuzz

from app.services.rate_limiter import saij_limiter

_SEARCH_URL = "https://saij.gob.ar/busqueda"
_BASE = "https://saij.gob.ar"
_TIMEOUT = 20.0
_JURISP_FACET = "Tipo de Documento/Jurisprudencia[1,1]"


class SourceResult(TypedDict):
    found: bool
    canonical_caratula: str | None
    ruling_text: str | None
    source: str
    source_url: str | None
    match_score: float


def _extract_year(year_tomo_folio: str) -> str:
    m = re.search(r"\b(19|20)\d{2}\b", year_tomo_folio or "")
    return m.group(0) if m else ""


def _parse_api_response(data: dict, case_name: str) -> list[SourceResult]:
    results: list[SourceResult] = []
    doc_list = (data.get("searchResults") or {}).get("documentResultList") or []

    for item in doc_list:
        raw_abstract = item.get("documentAbstract", "")
        try:
            abstract = json.loads(raw_abstract) if isinstance(raw_abstract, str) else raw_abstract
        except (json.JSONDecodeError, TypeError):
            continue

        doc = abstract.get("document", abstract)
        if not isinstance(doc, dict):
            continue

        content = doc.get("content", {})
        meta = doc.get("metadata", {})

        actor = (content.get("actor") or "").strip()
        sobre = (content.get("sobre") or "").strip()
        if not actor:
            continue

        caratula = f"{actor} {sobre}".strip() if sobre else actor

        source_url = f"{_BASE}/buscador/jurisprudencia-nacional?busqueda={urllib.parse.quote(caratula)}"

        score = fuzz.WRatio(case_name.lower(), caratula.lower()) / 100.0
        results.append(
            SourceResult(
                found=True,
                canonical_caratula=caratula,
                ruling_text=None,  # SAIJ exposes no sumario text; detail endpoints return 500
                source="SAIJ",
                source_url=source_url,
                match_score=score,
            )
        )

    return results


async def fetch(citation: dict, client: httpx.AsyncClient | None = None) -> list[SourceResult]:
    case_name = citation.get("case_name", "")
    year_tomo_folio = citation.get("year_tomo_folio") or ""
    year = _extract_year(year_tomo_folio)

    query = f"{case_name} {year}".strip()

    owns_client = client is None
    if owns_client:
        # SAIJ has an expired/self-signed cert; verify=False is intentional
        client = httpx.AsyncClient(timeout=_TIMEOUT, follow_redirects=True, verify=False)

    try:
        async with saij_limiter:
            params = {
                "q": query,
                "f": _JURISP_FACET,
                "p": "5",
                "o": "0",
            }
            resp = await client.get(_SEARCH_URL, params=params)
            resp.raise_for_status()

        data = resp.json()
        candidates = _parse_api_response(data, case_name)
        return sorted(candidates, key=lambda r: r["match_score"], reverse=True)[:5]

    except Exception:
        return []
    finally:
        if owns_client:
            await client.aclose()
