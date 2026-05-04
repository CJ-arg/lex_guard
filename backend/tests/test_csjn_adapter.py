import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services.csjn_adapter import _parse_json_results, _parse_tomo_pagina, fetch


def test_parse_tomo_pagina_fallos_format():
    assert _parse_tomo_pagina("Fallos: 330:4921") == ("330", "4921")


def test_parse_tomo_pagina_bare_format():
    assert _parse_tomo_pagina("330:4921") == ("330", "4921")


def test_parse_tomo_pagina_returns_none_on_no_match():
    assert _parse_tomo_pagina("1957") is None
    assert _parse_tomo_pagina("") is None


_SAMPLE_RECORDS = [
    {
        "autos": "Siri, Ángel s/ interpone recurso de hábeas corpus",
        "texto": "Las garantías constitucionales son operativas y de aplicación directa.",
        "tomo": "239",
        "pagina": "459",
    },
    {
        "autos": "Kot S.R.L. c/ Estado Nacional",
        "texto": "La garantía constitucional del artículo 18 se extiende al domicilio comercial.",
        "tomo": "241",
        "pagina": "291",
    },
]


def test_parse_json_results_extracts_records():
    results = _parse_json_results(_SAMPLE_RECORDS, "Siri Angel")
    assert len(results) == 2


def test_parse_json_results_scores_best_match_first():
    results = _parse_json_results(_SAMPLE_RECORDS, "Siri Angel")
    assert results[0]["canonical_caratula"].startswith("Siri")


def test_parse_json_results_builds_source_url():
    results = _parse_json_results(_SAMPLE_RECORDS, "Siri Angel")
    for r in results:
        assert r["source_url"] is not None
        assert r["source_url"].startswith("https://")
        assert "verFallo" in r["source_url"]


def test_parse_json_results_empty_returns_empty():
    assert _parse_json_results([], "test") == []


def test_parse_json_results_skips_record_without_autos():
    records = [{"texto": "some text", "tomo": "1", "pagina": "1"}]
    assert _parse_json_results(records, "test") == []


def test_fetch_returns_empty_on_http_error():
    async def run():
        mock_client = AsyncMock()
        mock_client.get.side_effect = Exception("network error")
        mock_client.aclose = AsyncMock()
        with patch("app.services.csjn_adapter.csjn_limiter") as mock_lim:
            mock_lim.__aenter__ = AsyncMock(return_value=None)
            mock_lim.__aexit__ = AsyncMock(return_value=False)
            return await fetch({"case_name": "Siri Angel"}, client=mock_client)

    assert asyncio.run(run()) == []


def test_fetch_returns_parsed_results():
    async def run():
        mock_json_resp = MagicMock()
        mock_json_resp.json.return_value = _SAMPLE_RECORDS
        mock_json_resp.raise_for_status = MagicMock()

        mock_get_session = MagicMock()
        mock_post_resp = MagicMock()

        mock_client = AsyncMock()
        # get called twice: session GET, then paginarSumarios GET
        mock_client.get = AsyncMock(side_effect=[mock_get_session, mock_json_resp])
        mock_client.post = AsyncMock(return_value=mock_post_resp)
        mock_client.aclose = AsyncMock()

        with patch("app.services.csjn_adapter.csjn_limiter") as mock_lim:
            mock_lim.__aenter__ = AsyncMock(return_value=None)
            mock_lim.__aexit__ = AsyncMock(return_value=False)
            return await fetch({"case_name": "Siri Angel", "year_tomo_folio": "1957"}, client=mock_client)

    results = asyncio.run(run())
    assert len(results) > 0
    assert results[0]["source"] == "CSJN"
