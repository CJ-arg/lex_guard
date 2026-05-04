"""CSJN Secretaría de Jurisprudencia adapter.

Two-step flow:
  1. GET /sjconsulta/consultaSumarios/buscarSumarios.html → establishes SJCONSULTASESSION
  2. POST /sjconsulta/consultaSumarios/buscar.html with filter.autos=<case_name>
  3. GET /sjconsulta/consultaSumarios/paginarSumarios.html?startIndex=0 → JSON array

JSON record fields: autos (carátula), caratulaWeb, texto (ruling excerpt), tomo, pagina.
"""

import re
from typing import TypedDict

import httpx
from rapidfuzz import fuzz

from app.services.rate_limiter import csjn_limiter

_BASE = "https://sjconsulta.csjn.gov.ar/sjconsulta"
_SEARCH_PAGE = f"{_BASE}/consultaSumarios/buscarSumarios.html"
_BUSCAR_URL = f"{_BASE}/consultaSumarios/buscar.html"
_PAGINAR_URL = f"{_BASE}/consultaSumarios/paginarSumarios.html"
_FALLO_URL = "https://sjconsulta.csjn.gov.ar/sjconsulta/fallos/verFallo.html"
_TIMEOUT = 20.0


class SourceResult(TypedDict):
    found: bool
    canonical_caratula: str | None
    ruling_text: str | None
    source: str
    source_url: str | None
    match_score: float


def _parse_tomo_pagina(year_tomo_folio: str) -> tuple[str, str] | None:
    """Extract tomo and página from strings like 'Fallos: 330:4921' or '330:4921'."""
    m = re.search(r"(\d+)\s*:\s*(\d+)", year_tomo_folio or "")
    if m:
        return m.group(1), m.group(2)
    return None


def _parse_json_results(records: list[dict], case_name: str) -> list[SourceResult]:
    results: list[SourceResult] = []
    for rec in records:
        caratula = rec.get("autos") or rec.get("caratulaWeb") or ""
        if not caratula:
            continue
        texto = (rec.get("texto") or "").strip()
        tomo = rec.get("tomo") or ""
        pagina = rec.get("pagina") or ""
        source_url = f"{_FALLO_URL}?id={tomo}-{pagina}" if tomo and pagina else None
        score = fuzz.token_sort_ratio(case_name.lower(), caratula.lower()) / 100.0
        results.append(
            SourceResult(
                found=True,
                canonical_caratula=caratula,
                ruling_text=texto[:2000] if texto else None,
                source="CSJN",
                source_url=source_url,
                match_score=score,
            )
        )
    return results


async def fetch(citation: dict, client: httpx.AsyncClient | None = None) -> list[SourceResult]:
    case_name = citation.get("case_name", "")
    year_tomo_folio = citation.get("year_tomo_folio") or ""

    owns_client = client is None
    if owns_client:
        client = httpx.AsyncClient(timeout=_TIMEOUT, follow_redirects=True)

    try:
        async with csjn_limiter:
            # Step 1: establish session cookie
            await client.get(_SEARCH_PAGE)

            # Step 2: POST search form
            form_data: dict[str, str] = {"filter.autos": case_name}
            tomo_pagina = _parse_tomo_pagina(year_tomo_folio)
            if tomo_pagina:
                form_data["filter.tomo"] = tomo_pagina[0]
                form_data["filter.pagina"] = tomo_pagina[1]

            await client.post(_BUSCAR_URL, data=form_data)

            # Step 3: paginated JSON results
            resp = await client.get(_PAGINAR_URL, params={"startIndex": "0"})
            resp.raise_for_status()

        data = resp.json()
        if isinstance(data, list):
            records = data
        else:
            records = (
                data.get("sumarios")
                or data.get("results")
                or data.get("items")
                or []
            )

        candidates = _parse_json_results(records, case_name)
        return sorted(candidates, key=lambda r: r["match_score"], reverse=True)[:5]

    except Exception:
        return []
    finally:
        if owns_client:
            await client.aclose()
