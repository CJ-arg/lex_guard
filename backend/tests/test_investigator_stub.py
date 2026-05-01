from app.services.agent_investigator_stub import investigate_citations

KNOWN_CITATION = {
    "claim": "las garantías constitucionales son operativas",
    "case_name": "Siri Angel",
    "court": "CSJN",
    "year_tomo_folio": "1957",
}

UNKNOWN_CITATION = {
    "claim": "alguna afirmación",
    "case_name": "Expediente Inexistente c/ Nadie s/ Nada",
    "court": "Juzgado Civil N° 99",
    "year_tomo_folio": None,
}


def test_known_case_is_found():
    results = investigate_citations([KNOWN_CITATION])
    assert results[0]["found"] is True


def test_known_case_has_ruling_text():
    results = investigate_citations([KNOWN_CITATION])
    assert results[0]["ruling_text"] is not None
    assert len(results[0]["ruling_text"]) > 10


def test_unknown_case_not_found():
    results = investigate_citations([UNKNOWN_CITATION])
    assert results[0]["found"] is False


def test_unknown_case_ruling_text_is_none():
    results = investigate_citations([UNKNOWN_CITATION])
    assert results[0]["ruling_text"] is None


def test_original_fields_preserved():
    results = investigate_citations([KNOWN_CITATION])
    for field in ("claim", "case_name", "court", "year_tomo_folio"):
        assert results[0][field] == KNOWN_CITATION[field]


def test_empty_list():
    assert investigate_citations([]) == []


def test_multiple_citations():
    results = investigate_citations([KNOWN_CITATION, UNKNOWN_CITATION])
    assert results[0]["found"] is True
    assert results[1]["found"] is False
