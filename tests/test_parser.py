"""Tests for document parsers (PDF / DOCX / TXT)."""

from pathlib import Path

import pytest

from app.parser import extract_text, is_supported
from app.parser.text_parser import extract_txt_text

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"


# ---------------------------------------------------------------------------
# Test 8 from the evaluation plan: TXT parsing
# ---------------------------------------------------------------------------
def test_txt_extraction_returns_content():
    text = extract_txt_text(DATA_DIR / "jd" / "software_test_engineer.txt")
    assert "Software Test Automation Engineer" in text
    assert len(text) > 200


# ---------------------------------------------------------------------------
# Unsupported formats raise a clear error
# ---------------------------------------------------------------------------
def test_unsupported_extension_raises():
    with pytest.raises(ValueError):
        extract_text("resume.xyz")


def test_is_supported():
    assert is_supported("a.pdf")
    assert is_supported("b.docx")
    assert is_supported("c.txt")
    assert not is_supported("d.png")
    assert not is_supported("e.doc")


# ---------------------------------------------------------------------------
# Tests 6 & 7: PDF and DOCX parsing (uses the generated sample dataset)
# ---------------------------------------------------------------------------
def test_pdf_parsing():
    pdf_files = sorted((DATA_DIR / "resumes").glob("*.pdf"))
    assert pdf_files, "sample dataset missing -- run scripts/generate_sample_data.py"
    for pdf in pdf_files:
        text = extract_text(pdf)
        assert len(text) > 200, f"PDF text extraction too short for {pdf.name}"


def test_docx_parsing():
    docx_files = sorted((DATA_DIR / "resumes").glob("*.docx"))
    assert docx_files, "sample dataset missing -- run scripts/generate_sample_data.py"
    for docx in docx_files:
        text = extract_text(docx)
        assert len(text) > 200, f"DOCX text extraction too short for {docx.name}"


# ---------------------------------------------------------------------------
# Test 9: the whole 10+ resume batch parses
# ---------------------------------------------------------------------------
def test_sample_dataset_has_10_plus_resumes_and_all_parse():
    resumes = sorted(p for p in (DATA_DIR / "resumes").iterdir() if p.is_file() and is_supported(p))
    assert len(resumes) >= 10
    for resume in resumes:
        text = extract_text(resume)
        assert len(text) > 100, f"extraction failed for {resume.name}"
