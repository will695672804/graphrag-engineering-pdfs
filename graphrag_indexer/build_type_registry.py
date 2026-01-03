import pickle
import json
from collections import defaultdict, Counter
from pathlib import Path

GRAPH_PATH = "index/graph.pkl"
OUT_PATH = "index/type_registry.json"

with open(GRAPH_PATH, "rb") as f:
    G = pickle.load(f)

# ----------------------------
# Step 1: collect raw types
# ----------------------------
type_nodes = defaultdict(list)

for n, d in G.nodes(data=True):
    t = d.get("type", "UNKNOWN")
    type_nodes[t].append(n)

# ----------------------------
# Step 2: extract signatures
# ----------------------------
def node_signature(node):
    sig = {
        "out_rels": Counter(),
        "in_rels": Counter(),
        "attr_keys": set()
    }

    for _, _, ed in G.out_edges(node, data=True):
        sig["out_rels"][ed.get("relation", "UNKNOWN")] += 1

    for _, _, ed in G.in_edges(node, data=True):
        sig["in_rels"][ed.get("relation", "UNKNOWN")] += 1

    sig["attr_keys"] = set(G.nodes[node].keys()) - {"name", "type"}
    return sig


type_signatures = defaultdict(list)

for t, nodes in type_nodes.items():
    for n in nodes:
        type_signatures[t].append(node_signature(n))

# ----------------------------
# Step 3: aggregate type stats
# ----------------------------
registry = {}

for t, sigs in type_signatures.items():
    out_rel = Counter()
    in_rel = Counter()
    attr_keys = Counter()

    for s in sigs:
        out_rel.update(s["out_rels"])
        in_rel.update(s["in_rels"])
        attr_keys.update(s["attr_keys"])

    registry[t] = {
        "count": len(sigs),
        "common_out_relations": [r for r, _ in out_rel.most_common(10)],
        "common_in_relations": [r for r, _ in in_rel.most_common(10)],
        "common_attributes": [a for a, _ in attr_keys.most_common(10)]
    }

# ----------------------------
# Step 4: save registry
# ----------------------------
Path(OUT_PATH).parent.mkdir(parents=True, exist_ok=True)
with open(OUT_PATH, "w", encoding="utf-8") as f:
    json.dump(registry, f, indent=2)

print(f"[OK] Type registry written to {OUT_PATH}")
