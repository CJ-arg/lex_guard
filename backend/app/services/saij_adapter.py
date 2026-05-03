"""SAIJ (saij.gob.ar) adapter.

Searches jurisprudencia-nacional by carátula + año. Returns list of SourceResult dicts.
"""

import re
from typing import TypedDict

import httpx
from rapidfuzz import fuzz
from selectolax.parser import HTMLParser

from app.services.rate_limiter import saij_limiter

_SEARCH_URL = "https://saij.gob.ar/buscar"
_BASE = "https://saij.gob.ar"
_TIMEOUT = 15.0


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


def _parse_search_html(html: str, case_name: str) -> list[SourceResult]:
    tree = HTMLParser(html)
    results: list[SourceResult] = []

    # SAIJ result cards vary across redesigns; try common selectors
    items = (
        tree.css("article.resultado")
        or tree.css("div.resultado")
        or tree.css("li.resultado")
        or tree.css(".search-result")
        or tree.css("div[class*='result']")
    )

    for item in items:
        title_node = (
            item.css_first("h2")
            or item.css_first("h3")
            or item.css_first(".titulo")
            or item.css_first("a")
        )
        if not title_node:
            continue
        caratula = title_node.text(strip=True)
        if not caratula:
            continue

        link_node = item.css_first("a")
        source_url = None
        if link_node:
            href = link_node.attributes.get("href", "")
            if href and not href.startswith("javascript:"):
                source_url = href if href.startswith("http") else f"{_BASE}{href}"

        excerpt_node = item.css_first("p, .resumen, .extracto, .sumario")
        ruling_text = excerpt_node.text(strip=True) if excerpt_node else caratula

        score = fuzz.token_sort_ratio(case_name.lower(), caratula.lower()) / 100.0
        results.append(
            SourceResult(
                found=True,
                canonical_caratula=caratula,
                ruling_text=ruling_text[:2000],
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
        client = httpx.AsyncClient(timeout=_TIMEOUT, follow_redirects=True)

    try:
        async with saij_limiter:
            params = {
                "q": query,
                "tipo-documento": "jurisprudencia",
                "tipo-organismo": "nacional",
            }
            resp = await client.get(_SEARCH_URL, params=params)
            resp.raise_for_status()

        candidates = _parse_search_html(resp.text, case_name)
        return sorted(candidates, key=lambda r: r["match_score"], reverse=True)[:5]

    except Exception:
        return []
    finally:
        if owns_client:
            await client.aclose()
