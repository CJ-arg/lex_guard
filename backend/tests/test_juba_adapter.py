import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

from app.services.juba_adapter import _parse_results_html, fetch

_SAMPLE_HTML = """
<html><body>
<table id="grilla">
  <tr><td>Carátula</td><td>Sumario</td></tr>
  <tr>
    <td><a href="/ver?id=1">González, María c/ Municipalidad de La Plata</a></td>
    <td>El municipio es responsable por los daños causados en la vía pública.</td>
  </tr>
  <tr>
    <td><a href="/ver?id=2">Pérez, Juan c/ Provincia de Buenos Aires</a></td>
    <td>El Estado provincial debe garantizar el acceso a la justicia.</td>
  </tr>
</table>
</body></html>
"""


def test_parse_results_html_skips_header_row():
    results = _parse_results_html(_SAMPLE_HTML, "González María")
    # Header row with "Carátula" text is skipped
    assert all("Carátula" not in r["canonical_caratula"] for r in results)


def test_parse_results_html_extracts_rows():
    results = _parse_results_html(_SAMPLE_HTML, "González María")
    assert len(results) == 2


def test_parse_results_html_ranks_closest_match_first():
    results = _parse_results_html(_SAMPLE_HTML, "González María")
    assert "González" in results[0]["canonical_caratula"]


def test_parse_results_html_builds_absolute_url():
    results = _parse_results_html(_SAMPLE_HTML, "González María")
    for r in results:
        assert r["source_url"].startswith("https://")


def test_parse_results_html_empty_returns_empty():
    assert _parse_results_html("<html><body><table></table></body></html>", "test") == []


def test_fetch_returns_empty_on_error():
    async def run():
        mock_client = AsyncMock()
        mock_client.get.side_effect = Exception("connection refused")
        mock_client.aclose = AsyncMock()
        with patch("app.services.juba_adapter.juba_limiter") as mock_lim:
            mock_lim.__aenter__ = AsyncMock(return_value=None)
            mock_lim.__aexit__ = AsyncMock(return_value=False)
            return await fetch({"case_name": "González María"}, client=mock_client)

    assert asyncio.run(run()) == []


def test_fetch_parses_results():
    async def run():
        mock_resp = MagicMock()
        mock_resp.text = _SAMPLE_HTML
        mock_resp.raise_for_status = MagicMock()

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_resp)
        mock_client.aclose = AsyncMock()

        with patch("app.services.juba_adapter.juba_limiter") as mock_lim:
            mock_lim.__aenter__ = AsyncMock(return_value=None)
            mock_lim.__aexit__ = AsyncMock(return_value=False)
            return await fetch({"case_name": "González María"}, client=mock_client)

    results = asyncio.run(run())
    assert len(results) > 0
    assert results[0]["source"] == "JUBA"
