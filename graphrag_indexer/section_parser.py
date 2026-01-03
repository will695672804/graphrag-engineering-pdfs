# section_parser.py
import re

CHAPTER_RE = re.compile(r"^CHAPTER\s+(\d+)", re.IGNORECASE)
SECTION_RE = re.compile(r"^(\d+\.\d+)\s+(.+)")
SUBSECTION_RE = re.compile(r"^(\d+\.\d+\.\d+)\s+(.+)")

def parse_sections(pages):
    """
    pages: list of {page, text}
    returns: list of structured blocks
    """

    current = {
        "chapter": None,
        "section": None,
        "subsection": None,
        "text": [],
        "pages": set()
    }

    blocks = []

    def flush():
        if current["text"]:
            blocks.append({
                "chapter": current["chapter"],
                "section": current["section"],
                "subsection": current["subsection"],
                "pages": sorted(current["pages"]),
                "text": "\n".join(current["text"])
            })

    for p in pages:
        for line in p["text"].splitlines():
            line = line.strip()

            if CHAPTER_RE.match(line):
                flush()
                current = {
                    "chapter": line,
                    "section": None,
                    "subsection": None,
                    "text": [],
                    "pages": {p["page"]}
                }

            elif SUBSECTION_RE.match(line):
                flush()
                num, title = SUBSECTION_RE.match(line).groups()
                current = {
                    "chapter": current["chapter"],
                    "section": current["section"],
                    "subsection": f"{num} {title}",
                    "text": [],
                    "pages": {p["page"]}
                }

            elif SECTION_RE.match(line):
                flush()
                num, title = SECTION_RE.match(line).groups()
                current = {
                    "chapter": current["chapter"],
                    "section": f"{num} {title}",
                    "subsection": None,
                    "text": [],
                    "pages": {p["page"]}
                }
            else:
                current["text"].append(line)
                current["pages"].add(p["page"])

    flush()
    return blocks
