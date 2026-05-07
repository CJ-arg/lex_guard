import asyncio
from unittest.mock import AsyncMock, patch

import pytest

from app.services.investigator import investigate_citations

_CITATION_CSJN = {
    "claim": "las garantías constitucionales son operativas",
    "case_name": "Siri Angel",
    "court": "CSJN",
    "year_tomo_folio": "Fallos: 239:459",
}

_CITATION_SAIJ = {
    "claim": "la acción de clase procede",
    "case_name": "Halabi Ernesto",
    "court": "CNCiv",
    "year_tomo_folio": "2009",
}

_CITATION_UNKNOWN = {
    "claim": "alguna afirmación",
    "case_name": "Foo Bar",
    "court": "",
    "year_tomo_folio": "",
}

_CSJN_RESULT = {
    "found": True,
    "canonical_caratula": "Siri, Ángel s/ interpone recurso de hábeas corpus",
    "ruling_text": "Las garantías son de aplicación directa.",
    "source": "CSJN",
    "source_url": None,
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


# ------------------------------------------------------------------
# Router integration: CSJN citation goes to CSJN primary only
# ------------------------------------------------------------------

def test_csjn_citation_calls_only_csjn_when_found():
    patches = _patch_all(csjn=[_CSJN_RESULT])
    with patches["get_cached"], patches["set_cached"], \
         patches["csjn_fetch"] as mock_csjn, \
         patches["saij_fetch"] as mock_saij, \
         patches["juba_fetch"] as mock_juba:
        results = asyncio.run(investigate_citations([_CITATION_CSJN]))

    assert results[0]["found"] is True
    assert results[0]["source"] == "CSJN"
    mock_csjn.assert_called_once()
    mock_saij.assert_not_called()
    mock_juba.assert_not_called()


def test_csjn_citation_falls_to_secondary_when_primary_empty():
    patches = _patch_all(csjn=[], saij=[_SAIJ_RESULT])
    with patches["get_cached"], patches["set_cached"], \
         patches["csjn_fetch"] as mock_csjn, \
         patches["saij_fetch"] as mock_saij, \
         patches["juba_fetch"] as mock_juba:
        results = asyncio.run(investigate_citations([_CITATION_CSJN]))

    assert results[0]["found"] is True
    assert results[0]["source"] == "SAIJ"
    mock_csjn.assert_called_once()
    mock_saij.assert_called_once()
    mock_juba.assert_not_called()


# ------------------------------------------------------------------
# Router integration: unknown court uses fan-out
# ------------------------------------------------------------------

def test_unknown_court_fans_out_to_all():
    patches = _patch_all(csjn=[_CSJN_RESULT])
    with patches["get_cached"], patches["set_cached"], \
         patches["csjn_fetch"] as mock_csjn, \
         patches["saij_fetch"] as mock_saij, \
         patches["juba_fetch"] as mock_juba:
        results = asyncio.run(investigate_citations([_CITATION_UNKNOWN]))

    mock_csjn.assert_called_once()
    mock_saij.assert_called_once()
    mock_juba.assert_called_once()


# ------------------------------------------------------------------
# source_routing field
# ------------------------------------------------------------------

def test_source_routing_primary_found():
    patches = _patch_all(csjn=[_CSJN_RESULT])
    with patches["get_cached"], patches["set_cached"], \
         patches["csjn_fetch"], patches["saij_fetch"], patches["juba_fetch"]:
        results = asyncio.run(investigate_citations([_CITATION_CSJN]))

    sr = results[0]["source_routing"]
    assert sr["primary_attempted"] == "CSJN"
    assert sr["primary_result"] == "found"
    assert sr["secondary_attempted"] is None
    assert sr["fallback_used"] is False


def test_source_routing_secondary_used():
    patches = _patch_all(csjn=[], saij=[_SAIJ_RESULT])
    with patches["get_cached"], patches["set_cached"], \
         patches["csjn_fetch"], patches["saij_fetch"], patches["juba_fetch"]:
        results = asyncio.run(investigate_citations([_CITATION_CSJN]))

    sr = results[0]["source_routing"]
    assert sr["primary_result"] == "not_found"
    assert sr["secondary_attempted"] == "SAIJ"
    assert sr["secondary_result"] == "found"


def test_source_routing_fallback():
    patches = _patch_all(csjn=[_CSJN_RESULT])
    with patches["get_cached"], patches["set_cached"], \
         patches["csjn_fetch"], patches["saij_fetch"], patches["juba_fetch"]:
        results = asyncio.run(investigate_citations([_CITATION_UNKNOWN]))

    assert results[0]["source_routing"]["fallback_used"] is True


# ------------------------------------------------------------------
# Scoring / unverifiable
# ------------------------------------------------------------------

def test_below_threshold_returns_unverifiable():
    low = {**_CSJN_RESULT, "match_score": 0.79}
    patches = _patch_all(csjn=[low])
    with patches["get_cached"], patches["set_cached"], \
         patches["csjn_fetch"], patches["saij_fetch"], patches["juba_fetch"]:
        results = asyncio.run(investigate_citations([_CITATION_CSJN]))

    assert results[0]["unverifiable"] is True


def test_prefers_csjn_over_saij_when_both_pass():
    patches = _patch_all(csjn=[_CSJN_RESULT], saij=[_SAIJ_RESULT])
    with patches["get_cached"], patches["set_cached"], \
         patches["csjn_fetch"], patches["saij_fetch"], patches["juba_fetch"]:
        # fan-out via unknown court
        citation = {**_CITATION_UNKNOWN, "case_name": "Siri Angel"}
        results = asyncio.run(investigate_citations([citation]))

    assert results[0]["source"] == "CSJN"


def test_cache_hit_skips_adapters():
    cache_row = {
        "source": "SAIJ",
        "source_url": None,
        "canonical_caratula": "Siri, Ángel",
        "ruling_text": "texto",
        "match_score": 0.95,
        "source_routing": None,
    }
    patches = _patch_all(cache_hit=cache_row)
    with patches["get_cached"], patches["set_cached"] as mock_set, \
         patches["csjn_fetch"] as mock_csjn, \
         patches["saij_fetch"] as mock_saij, \
         patches["juba_fetch"] as mock_juba:
        results = asyncio.run(investigate_citations([_CITATION_CSJN]))

    mock_csjn.assert_not_called()
    mock_saij.assert_not_called()
    mock_juba.assert_not_called()
    mock_set.assert_not_called()
    assert results[0]["source"] == "SAIJ"


def test_empty_citations_list():
    assert asyncio.run(investigate_citations([])) == []


def test_original_fields_preserved():
    patches = _patch_all(csjn=[_CSJN_RESULT])
    with patches["get_cached"], patches["set_cached"], \
         patches["csjn_fetch"], patches["saij_fetch"], patches["juba_fetch"]:
        results = asyncio.run(investigate_citations([_CITATION_CSJN]))

    for field in ("claim", "case_name", "court", "year_tomo_folio"):
        assert results[0][field] == _CITATION_CSJN[field]


def test_unverifiable_citation_judge_sets_correct_verdict():
    from app.services.agent_judge import judge_citations

    citation = {**_CITATION_CSJN, "found": False, "unverifiable": True, "ruling_text": None}
    results = judge_citations([citation])
    assert results[0]["verdict"] == "unverifiable"
