"""PDF text extraction built on PyMuPDF (fitz)."""

from pathlib import Path
from typing import Union


def extract_pdf_text(path: Union[str, Path]) -> str:
    try:
        import fitz  # PyMuPDF
    except ImportError as exc:  # pragma: no cover
        raise ImportError(
            "PyMuPDF is required to parse PDF files. Install it with: pip install pymupdf"
        ) from exc

    document = fitz.open(str(path))
    try:
        parts = []
        for page in document:
            text = page.get_text("text")
            if text:
                parts.append(text)
        return "\n".join(parts).strip()
    finally:
        document.close()
