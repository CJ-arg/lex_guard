"""JUBA (juba.scba.gov.ar) adapter.

Searches by carátula. Returns list of SourceResult dicts.
"""

from typing import TypedDict

import httpx
from rapidfuzz import fuzz
from selectolax.parser import HTMLParser

from app.services.rate_limiter import juba_limiter

_SEARCH_URL = "https://juba.scba.gov.ar/busquedas.aspx"
_BASE = "https://juba.scba.gov.ar"
_TIMEOUT = 15.0


class SourceResult(TypedDict):
    found: bool
    canonical_caratula: str | None
    ruling_text: str | None
    source: str
    source_url: str | None
    match_score: float


def _parse_results_html(html: str, case_name: str) -> list[SourceResult]:
    tree = HTMLParser(html)
    results: list[SourceResult] = []

    # JUBA renders results in a summary table; try common row selectors
    rows = (
        tree.css("table#grilla tr")
        or tree.css("table.grilla tr")
        or tree.css("table tr")
    )

    for row in rows:
        cells = row.css("td")
        if not cells:
            continue
        caratula_cell = cells[0]
        caratula = caratula_cell.text(strip=True)
        if not caratula or caratula.lower() in ("carátula", "caratula"):
            continue

        link_node = caratula_cell.css_first("a")
        source_url = None
        if link_node:
            href = link_node.attributes.get("href", "")
            if href:
                source_url = href if href.startswith("http") else f"{_BASE}/{href.lstrip('/')}"

        ruling_text = cells[-1].text(strip=True) if len(cells) > 1 else caratula

        score = fuzz.token_sort_ratio(case_name.lower(), caratula.lower()) / 100.0
        results.append(
            SourceResult(
                found=True,
                canonical_caratula=caratula,
                ruling_text=ruling_text[:2000],
                source="JUBA",
                source_url=source_url,
                match_score=score,
            )
        )

    return results


async def fetch(citation: dict, client: httpx.AsyncClient | None = None) -> list[SourceResult]:
    case_name = citation.get("case_name", "")

    owns_client = client is None
    if owns_client:
        client = httpx.AsyncClient(timeout=_TIMEOUT, follow_redirects=True)

    try:
        async with juba_limiter:
            # JUBA accepts GET params for the search form
            params = {"caratula": case_name}
            resp = await client.get(_SEARCH_URL, params=params)
            resp.raise_for_status()

        candidates = _parse_results_html(resp.text, case_name)
        return sorted(candidates, key=lambda r: r["match_score"], reverse=True)[:5]

    except Exception:
        return []
    finally:
        if owns_client:
            await client.aclose()
