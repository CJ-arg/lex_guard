import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services.csjn_adapter import _parse_result_html, _parse_tomo_pagina, fetch


def test_parse_tomo_pagina_fallos_format():
    assert _parse_tomo_pagina("Fallos: 330:4921") == ("330", "4921")


def test_parse_tomo_pagina_bare_format():
    assert _parse_tomo_pagina("330:4921") == ("330", "4921")


def test_parse_tomo_pagina_returns_none_on_no_match():
    assert _parse_tomo_pagina("1957") is None
    assert _parse_tomo_pagina("") is None


_SAMPLE_HTML = """
<html><body>
<table class="tablaCuerpo">
  <tr>
    <td><a href="/fallos/ver?id=1">Siri, Ángel s/ interpone recurso de hábeas corpus</a></td>
    <td>Las garantías constitucionales son operativas y de aplicación directa.</td>
  </tr>
  <tr>
    <td><a href="/fallos/ver?id=2">Kot S.R.L. c/ Estado Nacional</a></td>
    <td>La garantía constitucional del artículo 18 se extiende al domicilio comercial.</td>
  </tr>
</table>
</body></html>
"""


def test_parse_result_html_extracts_rows():
    results = _parse_result_html(_SAMPLE_HTML, "Siri Angel")
    assert len(results) == 2


def test_parse_result_html_scores_best_match_first():
    results = _parse_result_html(_SAMPLE_HTML, "Siri Angel")
    # Siri should score higher than Kot against "Siri Angel"
    assert results[0]["canonical_caratula"].startswith("Siri")


def test_parse_result_html_builds_absolute_url():
    results = _parse_result_html(_SAMPLE_HTML, "Siri Angel")
    assert results[0]["source_url"].startswith("https://")


def test_parse_result_html_empty_html_returns_empty():
    assert _parse_result_html("<html><body></body></html>", "test") == []


def test_fetch_returns_empty_on_http_error():
    async def run():
        mock_client = AsyncMock()
        mock_client.get.side_effect = Exception("network error")
        mock_client.aclose = AsyncMock()
        with patch("app.services.csjn_adapter.csjn_limiter") as mock_lim:
            mock_lim.__aenter__ = AsyncMock(return_value=None)
            mock_lim.__aexit__ = AsyncMock(return_value=False)
            return await fetch({"case_name": "Siri Angel"}, client=mock_client)

    result = asyncio.run(run())
    assert result == []


def test_fetch_returns_parsed_results():
    async def run():
        mock_resp = MagicMock()
        mock_resp.text = _SAMPLE_HTML
        mock_resp.raise_for_status = MagicMock()

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_resp)
        mock_client.aclose = AsyncMock()

        with patch("app.services.csjn_adapter.csjn_limiter") as mock_lim:
            mock_lim.__aenter__ = AsyncMock(return_value=None)
            mock_lim.__aexit__ = AsyncMock(return_value=False)
            return await fetch({"case_name": "Siri Angel", "year_tomo_folio": "1957"}, client=mock_client)

    results = asyncio.run(run())
    assert len(results) > 0
    assert results[0]["source"] == "CSJN"
