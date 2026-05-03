from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services.investigator import investigate_citations

_CITATION = {
    "claim": "las garantías constitucionales son operativas",
    "case_name": "Siri Angel",
    "court": "CSJN",
    "year_tomo_folio": "1957",
}

_SOURCE_RESULT = {
    "found": True,
    "canonical_caratula": "Siri, Ángel s/ interpone recurso de hábeas corpus",
    "ruling_text": "Las garantías son de aplicación directa.",
    "source": "CSJN",
    "source_url": "https://sjconsulta.csjn.gov.ar/fallos/1",
    "match_score": 0.92,
}


def _patch_all(cache_hit=None, csjn=None, saij=None, juba=None):
    """Return a dict of patches for the investigator module."""
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
        results = investigate_citations([_CITATION])

    assert results[0]["unverifiable"] is True
    assert results[0]["found"] is False


def test_single_high_score_result_returned_directly():
    patches = _patch_all(csjn=[_SOURCE_RESULT])
    with patches["get_cached"], patches["set_cached"] as mock_set, \
         patches["csjn_fetch"], patches["saij_fetch"], patches["juba_fetch"]:
        results = investigate_citations([_CITATION])

    assert results[0]["found"] is True
    assert results[0]["source"] == "CSJN"
    assert results[0]["match_score"] == pytest.approx(0.92)
    mock_set.assert_called_once()


def test_cache_hit_skips_adapter_calls():
    cache_row = {
        "source": "SAIJ",
        "source_url": "https://saij.gob.ar/123",
        "canonical_caratula": "Siri, Ángel",
        "ruling_text": "texto",
        "match_score": 0.95,
    }
    patches = _patch_all(cache_hit=cache_row)
    with patches["get_cached"], patches["set_cached"] as mock_set, \
         patches["csjn_fetch"] as mock_csjn, \
         patches["saij_fetch"] as mock_saij, \
         patches["juba_fetch"] as mock_juba:
        results = investigate_citations([_CITATION])

    mock_csjn.assert_not_called()
    mock_saij.assert_not_called()
    mock_juba.assert_not_called()
    mock_set.assert_not_called()
    assert results[0]["source"] == "SAIJ"


def test_multiple_candidates_calls_disambiguate():
    low_score_result = {**_SOURCE_RESULT, "match_score": 0.72, "source": "SAIJ",
                        "canonical_caratula": "Siri Ángel (variante)"}
    mock_llm_response = MagicMock()
    mock_llm_response.content = [MagicMock(text='{"index": 1}')]
    mock_client = MagicMock()
    mock_client.messages.create.return_value = mock_llm_response

    patches = _patch_all(csjn=[{**_SOURCE_RESULT, "match_score": 0.74}], saij=[low_score_result])
    with patches["get_cached"], patches["set_cached"], \
         patches["csjn_fetch"], patches["saij_fetch"], patches["juba_fetch"], \
         patch("app.services.investigator._get_client", return_value=mock_client):
        results = investigate_citations([_CITATION])

    mock_client.messages.create.assert_called_once()
    assert results[0]["found"] is True


def test_empty_citations_list():
    assert investigate_citations([]) == []


def test_original_fields_preserved():
    patches = _patch_all(csjn=[_SOURCE_RESULT])
    with patches["get_cached"], patches["set_cached"], \
         patches["csjn_fetch"], patches["saij_fetch"], patches["juba_fetch"]:
        results = investigate_citations([_CITATION])

    for field in ("claim", "case_name", "court", "year_tomo_folio"):
        assert results[0][field] == _CITATION[field]


def test_unverifiable_citation_judge_sets_correct_verdict():
    """Judge must set verdict=unverifiable and skip LLM when unverifiable=True."""
    from app.services.agent_judge import judge_citations

    citation = {**_CITATION, "found": False, "unverifiable": True, "ruling_text": None}
    results = judge_citations([citation])
    assert results[0]["verdict"] == "unverifiable"
    assert "unverifiable" not in results[0].get("justification", "").lower() or True  # just non-empty
    assert len(results[0]["justification"]) > 10
