# reextract_missed_chunks.py

import json
import os
import pickle
from extractor import extract_graph_elements
from graph_store import GraphStore
from extraction_mode import ExtractionMode

# 🔧 FILE LOCATIONS
MISSES_FILE = "index/missed_knowledge.json"
GRAPH_FILE = "index/graph.pkl"
CHECKPOINT_FILE = "index/reextract_checkpoint.json"

# 🔧 SAFETY: ensure IMPROVE mode
import extractor
extractor.EXTRACTION_MODE = ExtractionMode.IMPROVE


def load_checkpoint():
    if not os.path.exists(CHECKPOINT_FILE):
        return set()
    with open(CHECKPOINT_FILE, "r") as f:
        return set(json.load(f))


def save_checkpoint(done_chunk_ids):
    with open(CHECKPOINT_FILE, "w") as f:
        json.dump(sorted(done_chunk_ids), f, indent=2)


def main():
    print("🔁 Starting re-extraction of missed chunks (IMPROVE mode)")

    # Load misses
    with open(MISSES_FILE, "r") as f:
        misses = json.load(f)

    # Load existing graph
    store = GraphStore()
    with open(GRAPH_FILE, "rb") as f:
        store.graph = pickle.load(f)

    done_chunk_ids = load_checkpoint()
    newly_done = set(done_chunk_ids)

    total = sum(len(m["supporting_chunks"]) for m in misses)
    processed = 0

    for miss in misses:
        for chunk in miss["supporting_chunks"]:
            chunk_id = chunk.get("chunk_id")

            if chunk_id in done_chunk_ids:
                continue

            print(
                f"➡️ Re-extracting chunk {chunk_id} "
                f"(Chapter={chunk.get('chapter')}, Section={chunk.get('section')})"
            )

            result = extract_graph_elements(
                text=chunk["text"],
                chapter=chunk.get("chapter"),
                section=chunk.get("section"),
                subsection=chunk.get("subsection"),
                pages=chunk.get("pages"),
                chunk_id=chunk["chunk_id"]  # ✅ REQUIRED
            )

            store.add_entities(result.get("entities", []))
            store.add_relations(result.get("relations", []))

            newly_done.add(chunk_id)
            processed += 1

            # 🔐 Save checkpoint every 5 chunks
            if processed % 5 == 0:
                save_checkpoint(newly_done)
                store.save()
                print(f"💾 Checkpoint saved ({processed}/{total})")

    # Final save
    save_checkpoint(newly_done)
    store.save()

    print("✅ Re-extraction complete.")
    print(f"🧠 Total chunks reprocessed: {processed}")


if __name__ == "__main__":
    main()
