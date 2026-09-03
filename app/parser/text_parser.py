"""Plain-text (TXT) extraction."""

from pathlib import Path
from typing import Union


def extract_txt_text(path: Union[str, Path]) -> str:
    with open(path, "r", encoding="utf-8", errors="ignore") as file:
        return file.read().strip()
