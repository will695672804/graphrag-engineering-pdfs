# table_extractor.py
import re

def looks_like_table(text: str) -> bool:
    # Heuristics: multiple columns / numeric density
    lines = text.splitlines()
    if len(lines) < 3:
        return False

    numeric_lines = sum(
        1 for l in lines if re.search(r"\d", l)
    )

    separators = sum(
        1 for l in lines if "|" in l or "\t" in l
    )

    return numeric_lines >= 2 and separators >= 1


def normalize_table_text(text: str) -> str:
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    return "\n".join(lines)
