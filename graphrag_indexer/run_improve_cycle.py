# run_improve_cycle.py
#
# End-to-end GraphRAG improvement cycle with:
# - strategy evaluation
# - semantic canonical learning
# - ontology-safe re-extraction
# - community rebuild
# - before/after comparison
#
# SAFE: no re-indexing, no embedding rebuilds

import os
import sys
import json
import subprocess
from datetime import datetime

from config import INDEX_DIR

ARCHIVE_DIR = f"{INDEX_DIR}/history"
STRATEGY_FILE = f"{INDEX_DIR}/strategy_comparison.json"

os.makedirs(ARCHIVE_DIR, exist_ok=True)


# ------------------------------------------------------------
# Utilities
# ------------------------------------------------------------

def run(script, desc):
    """
    Run a Python script using the *current* interpreter.
    Prevents Windows / conda interpreter mismatch bugs.
    """
    print(f"\n▶ {desc}")
    cmd = f'"{sys.executable}" {script}'
    result = subprocess.run(cmd, shell=True)
    if result.returncode != 0:
        raise RuntimeError(f"❌ Failed step: {desc}")


def load_json(path, default=None):
    if not os.path.exists(path):
        return default
    with open(path, "r") as f:
        return json.load(f)


def archive_file(path, tag):
    if not os.path.exists(path):
        return
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    base = os.path.basename(path)
    dst = f"{ARCHIVE_DIR}/{base.replace('.json', '')}_{tag}_{ts}.json"
    with open(path, "r") as src, open(dst, "w") as out:
        out.write(src.read())
    print(f"📦 Archived → {dst}")


def graph_only_failure_rate(results):
    """
    Compute how often graph-only fails to answer.
    """
    if not results:
        return 1.0

    failures = 0
    for r in results:
        ans = r.get("graph_only", "").lower()
        if "no information" in ans or "not provided" in ans:
            failures += 1

    return failures / len(results)


# ------------------------------------------------------------
# Main Improve Cycle
# ------------------------------------------------------------

def main():
    print("\n🚀 Starting GraphRAG Improve Cycle")

    # --------------------------------------------------------
    # 1️⃣ Initial strategy evaluation
    # --------------------------------------------------------
    run(
        "evaluate_strategies.py",
        "Running initial strategy comparison"
    )

    archive_file(STRATEGY_FILE, "before")

    results = load_json(STRATEGY_FILE, [])
    failure_rate = graph_only_failure_rate(results)

    print(f"\n📊 Graph-only failure rate: {failure_rate:.2%}")

    # --------------------------------------------------------
    # 2️⃣ Decide whether improvement is needed
    # --------------------------------------------------------
    if failure_rate < 0.20:
        print("✅ Graph-only performance acceptable. No improvement needed.")
        return

    # --------------------------------------------------------
    # 3️⃣ Learn semantic canonical entities & relations
    # --------------------------------------------------------
    run(
        "auto_canonical_generator.py",
        "Generating semantic canonical maps"
    )

    archive_file(f"{INDEX_DIR}/canonical_entities.json", "learned")
    archive_file(f"{INDEX_DIR}/canonical_relations.json", "learned")

    # --------------------------------------------------------
    # 4️⃣ Re-extract missed chunks using canonical maps
    # --------------------------------------------------------
    run(
        "reextract_missed_chunks.py",
        "Re-extracting missed chunks (canonicalized)"
    )

    # --------------------------------------------------------
    # 5️⃣ Rebuild communities
    # --------------------------------------------------------
    run(
        "build_communities_only.py",
        "Rebuilding graph communities"
    )

    # --------------------------------------------------------
    # 6️⃣ Re-evaluate strategies
    # --------------------------------------------------------
    run(
        "evaluate_strategies.py",
        "Re-running strategy comparison"
    )

    archive_file(STRATEGY_FILE, "after")

    print("\n🎉 Improve cycle complete.")


# ------------------------------------------------------------
if __name__ == "__main__":
    main()
