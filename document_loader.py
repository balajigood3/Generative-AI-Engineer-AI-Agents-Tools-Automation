"""Extract text from PDF, DOCX and TXT uploads."""
from io import BytesIO
from pathlib import Path
from pypdf import PdfReader
from docx import Document


def extract_text(filename: str, content: bytes) -> str:
    suffix = Path(filename).suffix.lower()
    if suffix == ".pdf":
        reader = PdfReader(BytesIO(content))
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    if suffix == ".docx":
        doc = Document(BytesIO(content))
        return "\n".join(p.text for p in doc.paragraphs)
    if suffix in {".txt", ".md"}:
        return content.decode("utf-8", errors="replace")
    raise ValueError("Supported file types: PDF, DOCX, TXT and MD.")
