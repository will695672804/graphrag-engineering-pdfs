# index_documents.py
import os,json
from text_loader import load_pages
from section_parser import parse_sections
from chunker import chunk_section
from extractor import extract_graph_elements
from graph_store import GraphStore
from community_detection import detect_communities
from summarizer import summarize_community
from config import INDEX_DIR
from vector_index import build_vector_index

SAVE_EVERY_CHUNKS = 25

def debug_print_extraction(chunk_id, entities, relations, max_items=5):
    print(f"\n📦 Chunk {chunk_id} extraction summary")
    print(f"   🧠 Entities extracted: {len(entities)}")
    for e in entities[:max_items]:
        print(f"     • [{e['type']}] {e['name']} ({e['id']})")

    if len(entities) > max_items:
        print(f"     … {len(entities) - max_items} more entities")

    print(f"   🔗 Relations extracted: {len(relations)}")
    for r in relations[:max_items]:
        print(f"     • ({r['type']}) {r['source']} → {r['target']}")

    if len(relations) > max_items:
        print(f"     … {len(relations) - max_items} more relations")

def verify_graph(store, chunk_id):
    nodes = store.graph.number_of_nodes()
    edges = store.graph.number_of_edges()

    print(
        f"🧪 Graph state after chunk {chunk_id}: "
        f"{nodes} nodes, {edges} edges"
    )

    if nodes == 0:
        raise RuntimeError(
            f"❌ Graph is empty after chunk {chunk_id}. "
            "Aborting to prevent data loss."
        )

def verify_graph_persistence():
    from graph_store import GraphStore
    s = GraphStore()
    s.load()

    if s.graph.number_of_nodes() == 0:
        raise RuntimeError(
            "❌ graph.pkl reload resulted in empty graph. "
            "Persistence is broken."
        )

    print(
        f"📥 Reload verification OK: "
        f"{s.graph.number_of_nodes()} nodes, "
        f"{s.graph.number_of_edges()} edges"
    )

def build_index(input_dir):
    checkpoint_path = f"{INDEX_DIR}/checkpoint.json"
    last_chunk_id = -1

    if os.path.exists(checkpoint_path):
        with open(checkpoint_path, "r") as f:
            last_chunk_id = json.load(f)["last_chunk_id"]
            print(f"🔁 Resuming from chunk {last_chunk_id}")
    pages = load_pages(input_dir)
    print(f"📄 Loaded {len(pages)} pages")

    blocks = parse_sections(pages)
    print(f"📚 Parsed {len(blocks)} section/subsection blocks")

    store = GraphStore()
    global_chunk_id = 0
    vector_chunks = []

    for b_idx, block in enumerate(blocks, start=1):
        chapter = block["chapter"]
        section = block["section"]
        subsection = block["subsection"]
        pages_span = block["pages"]
        # Skip front-matter / non-technical blocks
        if block["section"] is None:
            print(
                f"⏭️ Skipping Block {b_idx} (no section) | Pages {block['pages']}"
            )
            continue
        print(
            f"\n➡️ Ingesting Block {b_idx}/{len(blocks)} | "
            f"{chapter} | {section} | {subsection} | Pages {pages_span}"
        )

        chunks = chunk_section(block)

        for c_idx, ch in enumerate(chunks, start=1):

            # ✅ ALWAYS collect vector chunks (even on resume)
            vector_chunks.append({
                "text": ch["text"],
                "chapter": chapter,
                "section": section,
                "subsection": subsection,
                "pages": pages_span,
                "chunk_id": global_chunk_id
            })

            # ⏭️ Resume logic applies ONLY to graph extraction
            if global_chunk_id <= last_chunk_id:
                global_chunk_id += 1
                continue

            print(
                f"   🔹 Chunk {c_idx}/{len(chunks)} "
                f"(Global #{global_chunk_id})"
            )

            result = extract_graph_elements(
                text=ch["text"],
                chapter=chapter,
                section=section,
                subsection=subsection,
                pages=pages_span,
                chunk_id=global_chunk_id
            )

            id_map = store.add_entities(result.get("entities", []))
            store.add_relations(result.get("relations", []), id_map)

            debug_print_extraction(c_idx, result.get("entities", []), result.get("relations", []))

            if c_idx % 10 == 0:
                verify_graph(store, c_idx)

            if c_idx % 50 == 0:
                store.save()
                verify_graph_persistence()

            global_chunk_id += 1

            if global_chunk_id % SAVE_EVERY_CHUNKS == 0:
                print(f"💾 Checkpoint save at chunk {global_chunk_id}")
                store.save()
                with open(checkpoint_path, "w") as f:
                    json.dump({"last_chunk_id": global_chunk_id}, f)
    with open(checkpoint_path, "w") as f:
        json.dump({"last_chunk_id": global_chunk_id}, f)

    print(f"🧷 Final checkpoint saved at chunk {global_chunk_id}")

    # 🔐 FINAL SAVE (CRITICAL)
    print("💾 Final save of graph index...")
    store.save()
    print(f"✅ Graph index saved to {INDEX_DIR}")
    print("💾 Building vector index...")
    build_vector_index(vector_chunks)
    print("✅ Vector index saved")
    print("Building communities...")
    # -----------------------------
    # Community detection & summary
    # -----------------------------
    print("🧠 Detecting communities...")
    communities = detect_communities(store.graph)

    summaries = {}
    for cid in set(communities.values()):
        nodes = [n for n, c in communities.items() if c == cid]
        edges = list(store.graph.edges(nodes, data=True))
        if len(nodes) > 300 or len(edges) > 600:
            summaries[cid] = "Community too large to summarize reliably."
        else:
            summaries[cid] = summarize_community(nodes, edges)

    with open(f"{INDEX_DIR}/communities.json", "w") as f:
        json.dump(communities, f, indent=2)

    with open(f"{INDEX_DIR}/summaries.json", "w") as f:
        json.dump(summaries, f, indent=2)

    print("✅ Communities and summaries saved")


if __name__ == "__main__":
    inpDir = "../data/documents"
    build_index(inpDir)
