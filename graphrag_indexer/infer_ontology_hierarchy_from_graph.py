import pickle
import json
from collections import defaultdict, Counter
from pathlib import Path

GRAPH_PATH = "index/graph.pkl"
ONTOLOGY_PATH = "index/ontology.json"
OUT_PATH = "index/ontology_with_hierarchy.json"

with open(GRAPH_PATH, "rb") as f:
    G = pickle.load(f)

with open(ONTOLOGY_PATH, "r", encoding="utf-8") as f:
    ontology = json.load(f)

# -----------------------------
# Build type → relation signatures
# -----------------------------
type_relations = defaultdict(Counter)
type_counts = Counter()

for n, d in G.nodes(data=True):
    t = d.get("type")
    if not t:
        continue
    type_counts[t] += 1

    for _, _, ed in G.out_edges(n, data=True):
        rel = ed.get("relation")
        if rel:
            type_relations[t][rel] += 1

# -----------------------------
# Subtype inference (RELATION-BASED)
# -----------------------------
def is_subtype(child, parent):
    if child == parent:
        return False

    c_rels = set(type_relations[child].keys())
    p_rels = set(type_relations[parent].keys())

    if not c_rels or not p_rels:
        return False

    overlap = len(c_rels & p_rels) / len(c_rels)

    return (
        overlap >= 0.6 and
        type_counts[child] < type_counts[parent]
    )

subclasses = []

types = list(type_relations.keys())
for child in types:
    for parent in types:
        if is_subtype(child, parent):
            subclasses.append({
                "child": child,
                "parent": parent,
                "confidence": round(
                    len(set(type_relations[child]) & set(type_relations[parent])) /
                    len(set(type_relations[child])),
                    2
                )
            })

ontology["subclasses"] = subclasses

Path(OUT_PATH).parent.mkdir(exist_ok=True)

with open(OUT_PATH, "w", encoding="utf-8") as f:
    json.dump(ontology, f, indent=2)

print(f"[OK] Inferred {len(subclasses)} subclass relationships")
