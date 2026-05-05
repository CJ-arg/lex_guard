from app.db import get_conn


def save_session(document_name: str, user_note: str | None, citations: list[dict]) -> str:
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO sessions (document_name, user_note) VALUES (%s, %s) RETURNING id",
                (document_name, user_note),
            )
            session_id = str(cur.fetchone()["id"])

            for position, citation in enumerate(citations):
                import json as _json
                sr = citation.get("source_routing")
                cur.execute(
                    """
                    INSERT INTO citation_results
                      (session_id, position, claim, case_name, court, year_tomo_folio,
                       found, verdict, justification,
                       source, source_url, match_score, canonical_caratula, unverifiable,
                       source_routing)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        session_id,
                        position,
                        citation.get("claim", ""),
                        citation.get("case_name", ""),
                        citation.get("court"),
                        citation.get("year_tomo_folio"),
                        citation.get("found", False),
                        citation.get("verdict", "danger"),
                        citation.get("justification", ""),
                        citation.get("source"),
                        citation.get("source_url"),
                        citation.get("match_score"),
                        citation.get("canonical_caratula"),
                        bool(citation.get("unverifiable", False)),
                        _json.dumps(sr) if sr else None,
                    ),
                )
        conn.commit()
    finally:
        conn.close()
    return session_id


def get_session(session_id: str) -> dict:
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM sessions WHERE id = %s", (session_id,))
            session = cur.fetchone()
            if session is None:
                raise ValueError(f"Session {session_id} not found.")

            cur.execute(
                "SELECT * FROM citation_results WHERE session_id = %s ORDER BY position",
                (session_id,),
            )
            citations = cur.fetchall()
    finally:
        conn.close()

    return {
        "id": str(session["id"]),
        "document_name": session["document_name"],
        "user_note": session["user_note"],
        "created_at": session["created_at"].isoformat(),
        "citations": [
            {
                "claim": r["claim"],
                "case_name": r["case_name"],
                "court": r["court"],
                "year_tomo_folio": r["year_tomo_folio"],
                "found": r["found"],
                "verdict": r["verdict"],
                "justification": r["justification"],
                "source": r.get("source"),
                "source_url": r.get("source_url"),
                "match_score": r.get("match_score"),
                "canonical_caratula": r.get("canonical_caratula"),
                "unverifiable": bool(r.get("unverifiable", False)),
                "source_routing": r.get("source_routing"),
            }
            for r in citations
        ],
    }
