"""CSJN Secretaría de Jurisprudencia adapter.

Looks up a citation by Fallos: TOMO:PÁGINA when year_tomo_folio contains that format,
then falls back to a carátula search. Returns a list of SourceResult dicts.
"""

import re
from typing import TypedDict

import httpx
from rapidfuzz import fuzz
from selectolax.parser import HTMLParser

from app.services.rate_limiter import csjn_limiter

_BASE = "https://sjconsulta.csjn.gov.ar/sjconsulta/fallos"
_SEARCH_URL = "https://sjconsulta.csjn.gov.ar/sjconsulta/fallos/listarFallosByIdFallo.do"
_DETAIL_URL = "https://sjconsulta.csjn.gov.ar/sjconsulta/fallos/verFallo.html"
_TIMEOUT = 15.0


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


def _parse_result_html(html: str, case_name: str) -> list[SourceResult]:
    tree = HTMLParser(html)
    results: list[SourceResult] = []

    rows = tree.css("table.tablaCuerpo tr, table.resultados tr, tr.resultado")
    for row in rows:
        cells = row.css("td")
        if len(cells) < 2:
            continue
        caratula_node = cells[0]
        caratula = caratula_node.text(strip=True)
        if not caratula:
            continue

        link_node = caratula_node.css_first("a")
        source_url = None
        if link_node:
            href = link_node.attributes.get("href", "")
            if href:
                source_url = href if href.startswith("http") else f"https://sjconsulta.csjn.gov.ar{href}"

        # Grab first paragraph as ruling excerpt
        ruling_text = cells[-1].text(strip=True) or caratula_node.text(strip=True)

        score = fuzz.token_sort_ratio(case_name.lower(), caratula.lower()) / 100.0
        results.append(
            SourceResult(
                found=True,
                canonical_caratula=caratula,
                ruling_text=ruling_text[:2000],
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
            tomo_pagina = _parse_tomo_pagina(year_tomo_folio)
            if tomo_pagina:
                tomo, pagina = tomo_pagina
                params = {"idFalloMin": f"{tomo}-{pagina}", "idFalloMax": f"{tomo}-{pagina}"}
            else:
                params = {"caratula": case_name, "maxRows": "10"}

            resp = await client.get(_SEARCH_URL, params=params)
            resp.raise_for_status()

        candidates = _parse_result_html(resp.text, case_name)
        return sorted(candidates, key=lambda r: r["match_score"], reverse=True)[:5]

    except Exception:
        return []
    finally:
        if owns_client:
            await client.aclose()
