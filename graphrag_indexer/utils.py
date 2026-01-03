# utils.py
import re

def clean_pdf_text(text: str) -> str:
    # Fix hyphenated line breaks
    text = re.sub(r"-\n", "", text)

    # Normalize whitespace
    text = re.sub(r"\n{2,}", "\n", text)
    text = re.sub(r"[ \t]+", " ", text)

    return text.strip()
