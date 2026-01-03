# chunker.py
from config import CHUNK_SIZE


def chunk_section(block):
    """
    Fully backward-compatible chunker.

    Accepts:
    - dict with 'text' (+ optional metadata)
    - list of such dicts

    Returns:
    - list of chunk dicts with keys:
      text, chapter, section, subsection, pages
    """

    chunks = []

    # ----------------------------
    # Normalize input → list[dict]
    # ----------------------------
    if isinstance(block, dict):
        blocks = [block]
    elif isinstance(block, list):
        blocks = block
    else:
        raise TypeError(f"chunk_section expects dict or list, got {type(block)}")

    # ----------------------------
    # Process each block defensively
    # ----------------------------
    for b in blocks:
        if not isinstance(b, dict):
            continue  # skip garbage safely

        text = b.get("text", "")
        if not isinstance(text, str) or not text.strip():
            continue

        chapter = b.get("chapter")
        section = b.get("section")
        subsection = b.get("subsection")
        pages = b.get("pages")

        for i in range(0, len(text), CHUNK_SIZE):
            chunks.append({
                "text": text[i:i + CHUNK_SIZE],
                "chapter": chapter,
                "section": section,
                "subsection": subsection,
                "pages": pages
            })

    return chunks
