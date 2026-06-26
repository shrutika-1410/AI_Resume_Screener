import re
from pathlib import Path


def extract_text_from_pdf(filepath: str) -> str:
    """Extract text from a PDF file using PyMuPDF."""
    import fitz

    doc = fitz.open(filepath)
    pages = []
    for page in doc:
        pages.append(page.get_text())
    doc.close()
    return "\n".join(pages)


def extract_text_from_docx(filepath: str) -> str:
    """Extract text from a DOCX file using python-docx."""
    from docx import Document

    doc = Document(filepath)
    paragraphs = [p.text for p in doc.paragraphs]
    return "\n".join(paragraphs)


def extract_text(filepath: str) -> str:
    """Extract plain text from a resume file.

    Supports:
      - .txt   : plain text
      - .pdf   : PDF via PyMuPDF
      - .docx  : Word documents via python-docx
      - .doc   : Older Word format (best-effort via python-docx, may fail)
    """

    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"Resume file not found: {filepath}")

    suffix = path.suffix.lower()

    if suffix == ".pdf":
        return extract_text_from_pdf(filepath)
    elif suffix == ".docx":
        return extract_text_from_docx(filepath)
    elif suffix == ".doc":
        # Best-effort: python-docx sometimes handles .doc (if it's actually docx format)
        try:
            return extract_text_from_docx(filepath)
        except Exception:
            # Fallback to raw text read
            pass

    # .txt or fallback
    try:
        raw = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        raw = path.read_bytes().decode("utf-8", errors="ignore")

    # Normalize whitespace.
    text = re.sub(r"\s+", " ", raw).strip()
    return text

