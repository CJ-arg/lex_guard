import asyncio
from unittest.mock import AsyncMock, patch

import pytest

from app.services.investigator import investigate_citations

_CITATION = {
    "claim": "las garantías constitucionales son operativas",
    "case_name": "Siri Angel",
    "court": "CSJN",
    "year_tomo_folio": "1957",
}

# score >= MIN_SCORE (0.80) so it passes the threshold
_SOURCE_RESULT = {
    "found": True,
    "canonical_caratula": "Siri, Ángel s/ interpone recurso de hábeas corpus",
    "ruling_text": "Las garantías son de aplicación directa.",
    "source": "CSJN",
    "source_url": "https://sjconsulta.csjn.gov.ar/fallos/1",
    "match_score": 0.92,
}

_SAIJ_RESULT = {
    "found": True,
    "canonical_caratula": "Siri, Angel interpone recurso de habeas corpus",
    "ruling_text": None,
    "source": "SAIJ",
    "source_url": "https://saij.gob.ar/buscador/jurisprudencia-nacional?busqueda=Siri+Angel",
    "match_score": 0.85,
}


def _patch_all(cache_hit=None, csjn=None, saij=None, juba=None):
    return {
        "get_cached": patch("app.services.investigator.get_cached", return_value=cache_hit),
        "set_cached": patch("app.services.investigator.set_cached"),
        "csjn_fetch": patch(
            "app.services.investigator.csjn_adapter.fetch",
            new=AsyncMock(return_value=csjn or []),
        ),
        "saij_fetch": patch(
            "app.services.investigator.saij_adapter.fetch",
            new=AsyncMock(return_value=saij or []),
        ),
        "juba_fetch": patch(
            "app.services.investigator.juba_adapter.fetch",
            new=AsyncMock(return_value=juba or []),
        ),
    }


def test_all_adapters_fail_returns_unverifiable():
    patches = _patch_all()
    with patches["get_cached"], patches["set_cached"], \
         patches["csjn_fetch"], patches["saij_fetch"], patches["juba_fetch"]:
        results = asyncio.run(investigate_citations([_CITATION]))

    assert results[0]["unverifiable"] is True
    assert results[0]["found"] is False


def test_below_threshold_returns_unverifiable():
    low = {**_SOURCE_RESULT, "match_score": 0.79}
    patches = _patch_all(csjn=[low])
    with patches["get_cached"], patches["set_cached"], \
         patches["csjn_fetch"], patches["saij_fetch"], patches["juba_fetch"]:
        results = asyncio.run(investigate_citations([_CITATION]))

    assert results[0]["unverifiable"] is True


def test_high_score_result_returned():
    patches = _patch_all(csjn=[_SOURCE_RESULT])
    with patches["get_cached"], patches["set_cached"] as mock_set, \
         patches["csjn_fetch"], patches["saij_fetch"], patches["juba_fetch"]:
        results = asyncio.run(investigate_citations([_CITATION]))

    assert results[0]["found"] is True
    assert results[0]["source"] == "CSJN"
    assert results[0]["match_score"] == pytest.approx(0.92)
    mock_set.assert_called_once()


def test_prefers_csjn_over_saij_when_both_pass():
    """CSJN result has ruling_text; SAIJ does not — CSJN must win."""
    patches = _patch_all(csjn=[_SOURCE_RESULT], saij=[_SAIJ_RESULT])
    with patches["get_cached"], patches["set_cached"], \
         patches["csjn_fetch"], patches["saij_fetch"], patches["juba_fetch"]:
        results = asyncio.run(investigate_citations([_CITATION]))

    assert results[0]["source"] == "CSJN"
    assert results[0]["ruling_text"] is not None


def test_cache_hit_skips_adapter_calls():
    cache_row = {
        "source": "SAIJ",
        "source_url": "https://saij.gob.ar/buscador/jurisprudencia-nacional?busqueda=Siri+Angel",
        "canonical_caratula": "Siri, Ángel",
        "ruling_text": "texto",
        "match_score": 0.95,
    }
    patches = _patch_all(cache_hit=cache_row)
    with patches["get_cached"], patches["set_cached"] as mock_set, \
         patches["csjn_fetch"] as mock_csjn, \
         patches["saij_fetch"] as mock_saij, \
         patches["juba_fetch"] as mock_juba:
        results = asyncio.run(investigate_citations([_CITATION]))

    mock_csjn.assert_not_called()
    mock_saij.assert_not_called()
    mock_juba.assert_not_called()
    mock_set.assert_not_called()
    assert results[0]["source"] == "SAIJ"


def test_empty_citations_list():
    assert asyncio.run(investigate_citations([])) == []


def test_original_fields_preserved():
    patches = _patch_all(csjn=[_SOURCE_RESULT])
    with patches["get_cached"], patches["set_cached"], \
         patches["csjn_fetch"], patches["saij_fetch"], patches["juba_fetch"]:
        results = asyncio.run(investigate_citations([_CITATION]))

    for field in ("claim", "case_name", "court", "year_tomo_folio"):
        assert results[0][field] == _CITATION[field]


def test_unverifiable_citation_judge_sets_correct_verdict():
    from app.services.agent_judge import judge_citations

    citation = {**_CITATION, "found": False, "unverifiable": True, "ruling_text": None}
    results = judge_citations([citation])
    assert results[0]["verdict"] == "unverifiable"
    assert len(results[0]["justification"]) > 10
