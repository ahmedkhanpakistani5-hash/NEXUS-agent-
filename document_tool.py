import io

from docx import Document
from pypdf import PdfReader


def _clean_text(raw_text: str) -> str:
    return " ".join(raw_text.split())


def extract_document_text(uploaded_file) -> str:
    if uploaded_file is None:
        return ""

    file_name = (uploaded_file.name or "").lower()
    content = uploaded_file.getvalue()

    if not content:
        return ""

    if file_name.endswith(".pdf"):
        try:
            reader = PdfReader(io.BytesIO(content))
            pages = []
            for page in reader.pages:
                extracted = page.extract_text() or ""
                pages.append(extracted)
            return _clean_text("\n".join(pages))
        except Exception as exc:
            raise ValueError("Unable to process this document.") from exc

    if file_name.endswith(".docx"):
        try:
            doc = Document(io.BytesIO(content))
            paragraphs = [paragraph.text for paragraph in doc.paragraphs]
            return _clean_text("\n".join(paragraphs))
        except Exception as exc:
            raise ValueError("Unable to process this document.") from exc

    if file_name.endswith(".txt"):
        try:
            return _clean_text(content.decode("utf-8", errors="replace"))
        except Exception as exc:
            raise ValueError("Unable to process this document.") from exc

    raise ValueError("Unsupported file type. Please upload a PDF, DOCX, or TXT file.")
