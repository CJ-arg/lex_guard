from unittest.mock import MagicMock, patch

from app.services.agent_judge import judge_citations

NOT_FOUND_CITATION = {
    "claim": "alguna afirmación",
    "case_name": "Expediente Inexistente s/ Nada",
    "court": "Juzgado Civil N° 99",
    "year_tomo_folio": None,
    "found": False,
    "ruling_text": None,
}

FOUND_CITATION = {
    "claim": "las garantías constitucionales son operativas",
    "case_name": "Siri Angel",
    "court": "CSJN",
    "year_tomo_folio": "1957",
    "found": True,
    "ruling_text": "Las garantías constitucionales son de aplicación directa.",
}


def test_not_found_auto_danger():
    results = judge_citations([NOT_FOUND_CITATION])
    assert results[0]["verdict"] == "danger"


def test_not_found_has_justification():
    results = judge_citations([NOT_FOUND_CITATION])
    assert len(results[0]["justification"]) > 10


def _mock_client(text: str):
    mock_client = MagicMock()
    mock_client.messages.create.return_value = MagicMock(
        content=[MagicMock(text=text)]
    )
    return mock_client


def test_not_found_skips_api_call():
    with patch("app.services.agent_judge._get_client") as mock_get:
        judge_citations([NOT_FOUND_CITATION])
        mock_get.assert_not_called()


def test_found_citation_calls_api():
    with patch("app.services.agent_judge._get_client", return_value=_mock_client('{"verdict": "approved", "justification": "La cita es correcta."}')):
        results = judge_citations([FOUND_CITATION])

    assert results[0]["verdict"] == "approved"
    assert results[0]["justification"] == "La cita es correcta."


def test_original_fields_preserved():
    with patch("app.services.agent_judge._get_client", return_value=_mock_client('{"verdict": "warning", "justification": "Relación tangencial."}')):
        results = judge_citations([FOUND_CITATION])

    for field in ("claim", "case_name", "court", "found", "ruling_text"):
        assert results[0][field] == FOUND_CITATION[field]


def test_empty_list():
    assert judge_citations([]) == []


def test_mixed_citations():
    with patch("app.services.agent_judge._get_client", return_value=_mock_client('{"verdict": "approved", "justification": "Correcto."}')):
        results = judge_citations([NOT_FOUND_CITATION, FOUND_CITATION])

    assert results[0]["verdict"] == "danger"
    assert results[1]["verdict"] == "approved"


SAIJ_FOUND_CITATION = {
    "claim": "las garantías constitucionales son operativas",
    "case_name": "Siri Angel",
    "court": "CSJN",
    "year_tomo_folio": "1957",
    "found": True,
    "ruling_text": None,  # SAIJ confirms existence but provides no sumario text
    "source": "SAIJ",
}


def test_saij_found_no_text_is_warning():
    results = judge_citations([SAIJ_FOUND_CITATION])
    assert results[0]["verdict"] == "warning"


def test_saij_found_no_text_skips_api():
    with patch("app.services.agent_judge._get_client") as mock_get:
        judge_citations([SAIJ_FOUND_CITATION])
        mock_get.assert_not_called()


def test_saij_found_no_text_justification_mentions_source():
    results = judge_citations([SAIJ_FOUND_CITATION])
    j = results[0]["justification"]
    assert "localizado" in j or "texto" in j


UNVERIFIABLE_CITATION = {
    **NOT_FOUND_CITATION,
    "unverifiable": True,
}


def test_unverifiable_sets_verdict():
    results = judge_citations([UNVERIFIABLE_CITATION])
    assert results[0]["verdict"] == "unverifiable"


def test_unverifiable_skips_api_call():
    with patch("app.services.agent_judge._get_client") as mock_get:
        judge_citations([UNVERIFIABLE_CITATION])
        mock_get.assert_not_called()


def test_unverifiable_has_justification():
    results = judge_citations([UNVERIFIABLE_CITATION])
    assert len(results[0]["justification"]) > 10
