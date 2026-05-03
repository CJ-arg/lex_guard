import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

from app.services.saij_adapter import _extract_year, _parse_search_html, fetch

_SAMPLE_HTML = """
<html><body>
  <article class="resultado">
    <h2><a href="/jurisprudencia/siri-angel-123">Siri, Ángel s/ interpone recurso de hábeas corpus</a></h2>
    <p class="resumen">Las garantías constitucionales son operativas.</p>
  </article>
  <article class="resultado">
    <h2><a href="/jurisprudencia/halabi-456">Halabi, Ernesto c/ P.E.N.</a></h2>
    <p class="resumen">La acción de clase procede cuando existe hecho único.</p>
  </article>
</body></html>
"""


def test_extract_year_from_tomo_folio():
    assert _extract_year("Fallos: 330:4921") == ""  # no bare 4-digit year
    assert _extract_year("1994") == "1994"
    assert _extract_year("330:4921 año 2008") == "2008"


def test_parse_search_html_extracts_articles():
    results = _parse_search_html(_SAMPLE_HTML, "Siri Angel")
    assert len(results) == 2


def test_parse_search_html_ranks_siri_first():
    results = _parse_search_html(_SAMPLE_HTML, "Siri Angel")
    assert "Siri" in results[0]["canonical_caratula"]


def test_parse_search_html_builds_absolute_url():
    results = _parse_search_html(_SAMPLE_HTML, "Siri Angel")
    assert results[0]["source_url"].startswith("https://")


def test_parse_search_html_empty_returns_empty():
    assert _parse_search_html("<html><body></body></html>", "test") == []


def test_fetch_returns_empty_on_error():
    async def run():
        mock_client = AsyncMock()
        mock_client.get.side_effect = Exception("timeout")
        mock_client.aclose = AsyncMock()
        with patch("app.services.saij_adapter.saij_limiter") as mock_lim:
            mock_lim.__aenter__ = AsyncMock(return_value=None)
            mock_lim.__aexit__ = AsyncMock(return_value=False)
            return await fetch({"case_name": "Siri Angel"}, client=mock_client)

    assert asyncio.run(run()) == []


def test_fetch_parses_results():
    async def run():
        mock_resp = MagicMock()
        mock_resp.text = _SAMPLE_HTML
        mock_resp.raise_for_status = MagicMock()

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_resp)
        mock_client.aclose = AsyncMock()

        with patch("app.services.saij_adapter.saij_limiter") as mock_lim:
            mock_lim.__aenter__ = AsyncMock(return_value=None)
            mock_lim.__aexit__ = AsyncMock(return_value=False)
            return await fetch({"case_name": "Siri Angel", "year_tomo_folio": "1957"}, client=mock_client)

    results = asyncio.run(run())
    assert len(results) > 0
    assert results[0]["source"] == "SAIJ"
