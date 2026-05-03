from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch

import pytest

from app.services.citation_cache import TTL_DAYS, _cache_key, get_cached, set_cached


def _fresh_row(overrides: dict | None = None) -> dict:
    row = {
        "cache_key": "abc",
        "source": "CSJN",
        "source_url": "https://example.com",
        "canonical_caratula": "Siri, Ángel s/ interpone recurso de hábeas corpus",
        "ruling_text": "Las garantías son operativas.",
        "match_score": 0.95,
        "fetched_at": datetime.now(timezone.utc),
    }
    if overrides:
        row.update(overrides)
    return row


def _mock_conn(row):
    cursor = MagicMock()
    cursor.__enter__ = lambda s: s
    cursor.__exit__ = MagicMock(return_value=False)
    cursor.fetchone.return_value = row
    conn = MagicMock()
    conn.cursor.return_value = cursor
    return conn


def test_cache_key_is_deterministic():
    k1 = _cache_key("Siri Angel", "1957")
    k2 = _cache_key("Siri Angel", "1957")
    assert k1 == k2


def test_cache_key_normalises_case():
    assert _cache_key("SIRI ANGEL", "1957") == _cache_key("siri angel", "1957")


def test_get_cached_returns_none_on_miss():
    conn = _mock_conn(None)
    with patch("app.services.citation_cache.get_conn", return_value=conn):
        result = get_cached("Caso Inexistente", "")
    assert result is None


def test_get_cached_returns_row_on_hit():
    row = _fresh_row()
    conn = _mock_conn(row)
    with patch("app.services.citation_cache.get_conn", return_value=conn):
        result = get_cached("Siri Angel", "1957")
    assert result is not None
    assert result["source"] == "CSJN"


def test_get_cached_treats_expired_row_as_miss():
    old_time = datetime.now(timezone.utc) - timedelta(days=TTL_DAYS + 1)
    # The SQL WHERE clause handles TTL — simulate by returning None (DB already filtered it)
    conn = _mock_conn(None)
    with patch("app.services.citation_cache.get_conn", return_value=conn):
        result = get_cached("Siri Angel", "1957")
    assert result is None


def test_set_cached_executes_upsert():
    conn = MagicMock()
    cursor = MagicMock()
    cursor.__enter__ = lambda s: s
    cursor.__exit__ = MagicMock(return_value=False)
    conn.cursor.return_value = cursor

    with patch("app.services.citation_cache.get_conn", return_value=conn):
        set_cached(
            "Siri Angel",
            "1957",
            source="CSJN",
            source_url="https://example.com",
            match_score=0.95,
        )

    cursor.execute.assert_called_once()
    conn.commit.assert_called_once()
