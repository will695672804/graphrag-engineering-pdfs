# text_loader.py
from pathlib import Path
import fitz  # PyMuPDF
from config import INPUT_EXTENSIONS
from utils import clean_pdf_text

def load_text_from_pdf(pdf_path: Path) -> str:
    doc = fitz.open(pdf_path)
    pages_text = []

    for page in doc:
        text = page.get_text("text")  # "text" preserves reading order
        if text:
            pages_text.append(text)

    doc.close()

    full_text = "\n".join(pages_text)
    return clean_pdf_text(full_text)
def load_pages(input_dir):
    pages = []

    for path in Path(input_dir).rglob("*.pdf"):
        doc = fitz.open(path)
        for i, page in enumerate(doc, start=1):
            text = page.get_text("text")
            if text.strip():
                pages.append({
                    "source": str(path),
                    "page": i,
                    "text": text
                })
        doc.close()

    return pages

def load_documents(input_dir):
    docs = []

    for path in Path(input_dir).rglob("*"):
        if path.suffix.lower() not in INPUT_EXTENSIONS:
            continue

        if path.suffix.lower() == ".pdf":
            text = load_text_from_pdf(path)
        else:
            text = path.read_text(encoding="utf-8", errors="ignore")

        if not text.strip():
            continue

        docs.append({
            "path": str(path),
            "text": text
        })

    return docs
