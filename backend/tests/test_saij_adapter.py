import asyncio
import json
from unittest.mock import AsyncMock, MagicMock, patch

from app.services.saij_adapter import _extract_year, _parse_api_response, fetch

_SAMPLE_API_RESPONSE = {
    "searchResults": {
        "documentResultList": [
            {
                "documentScore": 0.9,
                "uuid": "abc-123",
                "documentAbstract": json.dumps({
                    "document": {
                        "metadata": {
                            "uuid": "abc-123",
                            "friendly-url": {
                                "subdomain": "sentencia",
                                "description": "corte-suprema-siri-angel-1957-12-27",
                            },
                        },
                        "content": {
                            "tribunal": "CORTE SUPREMA DE JUSTICIA DE LA NACION",
                            "tipo-fallo": "SENTENCIA",
                            "fecha": "1957-12-27",
                            "actor": "Siri, Angel",
                            "sobre": "interpone recurso de habeas corpus",
                        },
                    }
                }),
            },
            {
                "documentScore": 0.5,
                "uuid": "def-456",
                "documentAbstract": json.dumps({
                    "document": {
                        "metadata": {
                            "uuid": "def-456",
                            "friendly-url": {
                                "subdomain": "sentencia",
                                "description": "corte-suprema-halabi-2009-02-24",
                            },
                        },
                        "content": {
                            "tribunal": "CORTE SUPREMA DE JUSTICIA DE LA NACION",
                            "tipo-fallo": "SENTENCIA",
                            "fecha": "2009-02-24",
                            "actor": "Halabi, Ernesto",
                            "sobre": "recurso de hecho deducido",
                        },
                    }
                }),
            },
        ]
    }
}


def test_extract_year_from_tomo_folio():
    assert _extract_year("Fallos: 330:4921") == ""  # no bare 4-digit year
    assert _extract_year("1994") == "1994"
    assert _extract_year("330:4921 año 2008") == "2008"


def test_parse_api_response_extracts_records():
    results = _parse_api_response(_SAMPLE_API_RESPONSE, "Siri Angel")
    assert len(results) == 2


def test_parse_api_response_ranks_siri_first():
    results = _parse_api_response(_SAMPLE_API_RESPONSE, "Siri Angel")
    assert "Siri" in results[0]["canonical_caratula"]


def test_parse_api_response_builds_source_url():
    results = _parse_api_response(_SAMPLE_API_RESPONSE, "Siri Angel")
    assert results[0]["source_url"].startswith("https://saij.gob.ar/buscador/")


def test_parse_api_response_empty_returns_empty():
    assert _parse_api_response({}, "test") == []
    assert _parse_api_response({"searchResults": {"documentResultList": []}}, "test") == []


def test_parse_api_response_skips_record_without_actor():
    data = {
        "searchResults": {
            "documentResultList": [
                {
                    "documentAbstract": json.dumps({
                        "document": {
                            "metadata": {},
                            "content": {"tribunal": "CSJN", "sobre": "algo"},
                        }
                    })
                }
            ]
        }
    }
    assert _parse_api_response(data, "test") == []


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
        mock_resp.json.return_value = _SAMPLE_API_RESPONSE
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
