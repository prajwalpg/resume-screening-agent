"""Document parsing: PDF / DOCX / TXT -> raw text.

All downstream stages only ever see plain text, so adding a new input
format means adding one parser and registering it here.
"""

from pathlib import Path
from typing import Union

from .docx_parser import extract_docx_text
from .pdf_parser import extract_pdf_text
from .text_parser import extract_txt_text

SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".txt"}


def extract_text(path: Union[str, Path]) -> str:
    """Dispatch to the correct parser based on the file extension."""
    file_path = Path(path)
    extension = file_path.suffix.lower()

    if extension == ".pdf":
        return extract_pdf_text(file_path)
    if extension == ".docx":
        return extract_docx_text(file_path)
    if extension == ".txt":
        return extract_txt_text(file_path)

    raise ValueError(
        f"Unsupported file format: '{extension}'. Supported formats: PDF, DOCX, TXT."
    )


def is_supported(path: Union[str, Path]) -> bool:
    return Path(path).suffix.lower() in SUPPORTED_EXTENSIONS


__all__ = [
    "extract_text",
    "is_supported",
    "extract_pdf_text",
    "extract_docx_text",
    "extract_txt_text",
    "SUPPORTED_EXTENSIONS",
]
