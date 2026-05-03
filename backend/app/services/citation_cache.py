import hashlib
from datetime import datetime, timedelta, timezone

from app.db import get_conn

TTL_DAYS = 30


def _cache_key(caratula: str, tomo_folio: str) -> str:
    raw = f"{caratula.lower().strip()}|{tomo_folio.lower().strip()}"
    return hashlib.sha256(raw.encode()).hexdigest()


def get_cached(caratula: str, tomo_folio: str = "") -> dict | None:
    key = _cache_key(caratula, tomo_folio)
    cutoff = datetime.now(timezone.utc) - timedelta(days=TTL_DAYS)
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT * FROM citation_cache WHERE cache_key = %s AND fetched_at > %s",
                (key, cutoff),
            )
            row = cur.fetchone()
    finally:
        conn.close()
    return dict(row) if row else None


def set_cached(
    caratula: str,
    tomo_folio: str = "",
    *,
    source: str,
    source_url: str | None = None,
    canonical_caratula: str | None = None,
    ruling_text: str | None = None,
    match_score: float = 0.0,
) -> None:
    key = _cache_key(caratula, tomo_folio)
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO citation_cache
                  (cache_key, source, source_url, canonical_caratula, ruling_text, match_score)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (cache_key) DO UPDATE SET
                  source              = EXCLUDED.source,
                  source_url          = EXCLUDED.source_url,
                  canonical_caratula  = EXCLUDED.canonical_caratula,
                  ruling_text         = EXCLUDED.ruling_text,
                  match_score         = EXCLUDED.match_score,
                  fetched_at          = NOW()
                """,
                (key, source, source_url, canonical_caratula, ruling_text, match_score),
            )
        conn.commit()
    finally:
        conn.close()
