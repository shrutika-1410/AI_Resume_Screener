import re
from pathlib import Path


def extract_text(filepath: str) -> str:
    """Extract plain text from a resume file.

    Current implementation supports plain text (.txt) and falls back to
    a best-effort utf-8 read for any other file type.

    If you add PDF/DOCX support later, keep this function signature.
    """

    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"Resume file not found: {filepath}")

    suffix = path.suffix.lower()

    # Simple support for .txt and best-effort read otherwise.
    # (This project currently had an empty parser.py, which breaks imports.)
    try:
        raw = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        raw = path.read_bytes().decode("utf-8", errors="ignore")

    # Normalize whitespace.
    text = re.sub(r"\s+", " ", raw).strip()
    return text

