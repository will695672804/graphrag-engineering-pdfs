# reextract_missed_chunks.py
#
# Expectation-driven re-extraction:
# - Uses strategy_comparison.json to infer missing graph facts
# - Reprocesses chunks that SHOULD contain those facts
# - Forces extractor to materialize missing relations
#
# SAFE: does NOT rebuild embeddings or full index

import json
import os
import re

from extractor import extract_graph_elements
from graph_store import GraphStore
from text_loader import load_documents
from chunker import chunk_section
from config import INDEX_DIR
from extraction_mode import ExtractionMode
from vector_index import vector_search, get_chunk_lookup

STRATEGY_FILE = f"{INDEX_DIR}/strategy_comparison.json"


# ------------------------------------------------------------
# 1️⃣ Map questions → expected graph relations
# ------------------------------------------------------------

EXPECTED_RELATIONS = {
    "operating sequence": "hasOperatingSequence",
    "insulation failure": "failsDueTo",
    "sf6 leakage": "maintainedBy",
}

EXPECTED_TRIGGERS = {
    "hasOperatingSequence": [
        "operating sequence",
        "duty cycle",
        "o-t-co",
        "co-t-co",
    ],
    "failsDueTo": [
        "failure",
        "failed due to",
        "caused by",
        "reason for failure",
        "ageing",
    ],
    "maintainedBy": [
        "maintenance",
        "inspection",
        "leak",
        "leakage",
        "mitigation",
    ],
}

def infer_expectations(question: str):
    q = question.lower()
    for key, rel in EXPECTED_RELATIONS.items():
        if key in q:
            return rel
    return None


# ------------------------------------------------------------
# 2️⃣ Main re-extraction logic
# ------------------------------------------------------------

def main():
    print("🔁 Starting re-extraction of missed facts (EXPECTATION MODE)")

    if not os.path.exists(STRATEGY_FILE):
        print("⚠️ No strategy comparison found. Skipping re-extraction.")
        return

    with open(STRATEGY_FILE, "r") as f:
        results = json.load(f)

    # Identify which relations failed in graph-only
    missing_relations = set()

    for r in results:
        graph_ans = r.get("graph_only", "").lower()
        if "no information" in graph_ans or "not provided" in graph_ans:
            rel = infer_expectations(r.get("question", ""))
            if rel:
                missing_relations.add(rel)

    if not missing_relations:
        print("✅ No missing relations detected. Nothing to re-extract.")
        return

    print(f"🧠 Missing relations detected: {missing_relations}")

    # --------------------------------------------------------
    # Load documents + graph
    # --------------------------------------------------------

    # --------------------------------------------------------
    # Vector-anchored re-extraction (MINIMAL PATCH)
    # --------------------------------------------------------

    #from vector_store import VectorStore  # existing module used in querying

    print("🔎 Using vector index to localize re-extraction")

    store = GraphStore()
    store.load()

    # Identify failed questions (existing logic)
    failed_questions = []
    for r in results:
        graph_ans = r.get("graph_only", "").lower()
        if "no information" in graph_ans or "not provided" in graph_ans:
            failed_questions.append(r["question"])

    if not failed_questions:
        print("✅ No failed questions. Skipping re-extraction.")
        return

    TOP_K = 5
    WINDOW = 1
    candidate_chunk_ids = set()

    # ---- Vector-anchored chunk selection ----
    for question in failed_questions:
        hits = vector_search(question, top_k=TOP_K)
        for hit in hits:
            cid = hit["chunk_id"]
            for n in range(cid - WINDOW, cid + WINDOW + 1):
                if n >= 0:
                    candidate_chunk_ids.add(n)

    print(f"🧠 Candidate chunks identified: {sorted(candidate_chunk_ids)}")

    chunk_lookup = get_chunk_lookup()

    reprocessed = 0

    for chunk_id in sorted(candidate_chunk_ids):
        chunk = chunk_lookup.get(chunk_id)
        if not chunk:
            continue

        print(f"➡️ Re-extracting chunk {chunk_id}")

        result = extract_graph_elements(
            text=chunk["text"],
            chapter=chunk.get("chapter"),
            section=chunk.get("section"),
            subsection=chunk.get("subsection"),
            pages=chunk.get("pages"),
            chunk_id=chunk_id,
            mode=ExtractionMode.IMPROVE,
            expected_relations=list(missing_relations)
        )

        if result["entities"] or result["relations"]:
            store.add_entities(result["entities"])
            store.add_relations(result["relations"])
            reprocessed += 1

    store.save()

    print(f"✅ Re-extraction complete. Chunks reprocessed: {reprocessed}")

    print(f"🧠 Total chunks reprocessed: {reprocessed}")


# ------------------------------------------------------------
if __name__ == "__main__":
    main()
