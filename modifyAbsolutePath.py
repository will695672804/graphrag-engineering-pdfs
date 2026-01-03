"""
modifyAbsolutePath.py

Scan all files under a given root directory, find lines containing a search string,
and print:
- file path relative to the root
- line number
- matching line content
- equivalent root-relative path string

GitHub-safe (no absolute paths, no usernames).
"""

from pathlib import Path
import sys


def scan_files(root_dir: Path, search: str, encoding="utf-8"):
    root_dir = root_dir.resolve()

    for path in root_dir.rglob("*"):
        if not path.is_file():
            continue

        try:
            with path.open("r", encoding=encoding, errors="ignore") as f:
                for lineno, line in enumerate(f, start=1):
                    if search in line:
                        rel_path = path.relative_to(root_dir)
                        print(f"\nFILE: {rel_path}")
                        print(f"LINE {lineno}: {line.rstrip()}")
                        print(f"RELATIVE STRING: {rel_path.as_posix()}")

        except Exception:
            # Ignore unreadable/binary files
            continue


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage:")
        print("  python modifyAbsolutePath.py <ROOT_DIR> <SEARCH_STRING>")
        sys.exit(1)

    root = Path(sys.argv[1])
    search_string = sys.argv[2]

    if not root.exists():
        print(f"ERROR: Root directory does not exist: {root}")
        sys.exit(1)

    scan_files(root, search_string)
