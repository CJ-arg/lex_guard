"""Tests for Phase 8 input sanitization in main.py."""
import io
from unittest.mock import patch, MagicMock

import pytest
from fastapi.testclient import TestClient

from app.main import app, _sanitize_filename, MAX_TEXT_CHARS

client = TestClient(app)


# ------------------------------------------------------------------
# _sanitize_filename helper
# ------------------------------------------------------------------

def test_sanitize_filename_strips_null_bytes():
    assert "\x00" not in _sanitize_filename("doc\x00ument.pdf")


def test_sanitize_filename_replaces_forward_slash():
    assert "/" not in _sanitize_filename("../../etc/passwd.pdf")


def test_sanitize_filename_replaces_backslash():
    assert "\\" not in _sanitize_filename("..\\windows\\system32.pdf")


def test_sanitize_filename_limits_length():
    long_name = "a" * 300 + ".pdf"
    assert len(_sanitize_filename(long_name)) <= 255


def test_sanitize_filename_empty_returns_default():
    assert _sanitize_filename("") == "documento"
    assert _sanitize_filename("   ") == "documento"


# ------------------------------------------------------------------
# /upload — Spanish error messages
# ------------------------------------------------------------------

def test_upload_rejects_wrong_extension():
    data = {"file": ("malware.exe", b"data", "application/octet-stream")}
    res = client.post("/upload", files=data)
    assert res.status_code == 415
    assert "PDF" in res.json()["detail"] or "DOCX" in res.json()["detail"]


def test_upload_rejects_oversized_file():
    big = b"x" * (1 * 1024 * 1024 + 1)
    data = {"file": ("big.pdf", big, "application/pdf")}
    res = client.post("/upload", files=data)
    assert res.status_code == 413
    assert "1 MB" in res.json()["detail"]


# ------------------------------------------------------------------
# /extract — text truncation
# ------------------------------------------------------------------

def test_extract_truncates_text_to_limit():
    oversized = "a" * (MAX_TEXT_CHARS + 10_000)
    captured = {}

    def fake_extract(text: str) -> list:
        captured["len"] = len(text)
        return []

    with patch("app.main.extract_citations", side_effect=fake_extract):
        client.post("/extract", json={"text": oversized})

    assert captured["len"] == MAX_TEXT_CHARS


def test_extract_short_text_not_truncated():
    short = "texto corto"
    captured = {}

    def fake_extract(text: str) -> list:
        captured["len"] = len(text)
        return []

    with patch("app.main.extract_citations", side_effect=fake_extract):
        client.post("/extract", json={"text": short})

    assert captured["len"] == len(short)


# ------------------------------------------------------------------
# /sessions — Pydantic field limits
# ------------------------------------------------------------------

def _session_payload(**overrides):
    base = {
        "document_name": "Demanda Empresa SA",
        "user_note": None,
        "citations": [],
    }
    return {**base, **overrides}


def test_save_session_rejects_long_document_name():
    payload = _session_payload(document_name="x" * 256)
    res = client.post("/sessions", json=payload)
    assert res.status_code == 422


def test_save_session_rejects_long_user_note():
    payload = _session_payload(user_note="x" * 501)
    res = client.post("/sessions", json=payload)
    assert res.status_code == 422


def test_save_session_accepts_valid_note():
    payload = _session_payload(user_note="x" * 500)
    with patch("app.main.save_session", return_value="abc-123"):
        res = client.post("/sessions", json=payload)
    assert res.status_code == 200


# ------------------------------------------------------------------
# extractor.py — null byte stripping
# ------------------------------------------------------------------

def test_extract_pdf_strips_null_bytes():
    from app.services.extractor import extract_pdf
    import fitz

    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 50), "hola\x00mundo")
    buf = doc.tobytes()

    result = extract_pdf(buf)
    assert "\x00" not in result


def test_extract_docx_returns_text_without_null_bytes():
    # lxml blocks null bytes at write time, so they never appear in DOCX
    # output; this confirms the extractor produces clean text in the normal path.
    from app.services.extractor import extract_docx
    from docx import Document
    from io import BytesIO

    doc = Document()
    doc.add_paragraph("texto limpio sin nulos")
    buf = BytesIO()
    doc.save(buf)

    result = extract_docx(buf.getvalue())
    assert "\x00" not in result
    assert "texto limpio" in result
