import pickle
import json
from collections import defaultdict, Counter
from pathlib import Path

GRAPH_PATH = "index/graph.pkl"
OUT_PATH = "index/ontology.json"

# -----------------------------
# Load graph
# -----------------------------
with open(GRAPH_PATH, "rb") as f:
    G = pickle.load(f)

# -----------------------------
# Containers
# -----------------------------
classes = set()
instances = defaultdict(list)
data_properties = defaultdict(set)
object_properties = defaultdict(lambda: {"domain": Counter(), "range": Counter()})
subclasses = set()

# -----------------------------
# Process nodes
# -----------------------------
for node, attrs in G.nodes(data=True):
    node_type = attrs.get("type", "UNKNOWN")
    classes.add(node_type)
    instances[node_type].append(node)

    for k, v in attrs.items():
        if k not in {"type", "name"} and not isinstance(v, (dict, list)):
            data_properties[node_type].add(k)

# -----------------------------
# Process edges
# -----------------------------
for src, tgt, attrs in G.edges(data=True):
    rel = attrs.get("relation", "RELATED_TO")
    inferred = attrs.get("inferred", False)

    src_type = G.nodes[src].get("type", "UNKNOWN")
    tgt_type = G.nodes[tgt].get("type", "UNKNOWN")

    if rel == "is_a":
        subclasses.add((src_type, tgt_type))
        continue

    object_properties[rel]["domain"][src_type] += 1
    object_properties[rel]["range"][tgt_type] += 1

# -----------------------------
# Normalize ontology
# -----------------------------
ontology = {
    "classes": sorted(classes),

    "subclasses": [
        {"child": c, "parent": p}
        for c, p in sorted(subclasses)
        if c != p
    ],

    "object_properties": {
        rel: {
            "domain": [d for d, _ in obj["domain"].most_common(3)],
            "range": [r for r, _ in obj["range"].most_common(3)]
        }
        for rel, obj in object_properties.items()
    },

    "data_properties": {
        cls: sorted(props)
        for cls, props in data_properties.items()
    },

    "instances": {
        cls: inst[:50]  # limit to avoid huge files
        for cls, inst in instances.items()
    }
}

# -----------------------------
# Save ontology
# -----------------------------
Path(OUT_PATH).parent.mkdir(parents=True, exist_ok=True)

with open(OUT_PATH, "w", encoding="utf-8") as f:
    json.dump(ontology, f, indent=2)

print(f"[OK] Ontology written to {OUT_PATH}")
