from app.db import get_conn


def save_session(document_name: str, user_note: str | None, citations: list[dict]) -> str:
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO sessions (document_name, user_note) VALUES (%s, %s) RETURNING id",
                (document_name, user_note),
            )
            session_id = str(cur.fetchone()["id"])

            for position, citation in enumerate(citations):
                cur.execute(
                    """
                    INSERT INTO citation_results
                      (session_id, position, claim, case_name, court, year_tomo_folio,
                       found, verdict, justification)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
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
                    ),
                )
        conn.commit()
    return session_id


def get_session(session_id: str) -> dict:
    with get_conn() as conn:
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
            }
            for r in citations
        ],
    }
