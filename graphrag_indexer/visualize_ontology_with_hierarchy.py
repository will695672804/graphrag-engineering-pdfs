import json
from pathlib import Path
from pyvis.network import Network

# ---------------- CONFIG ----------------
ONTOLOGY_PATH = "index/ontology_seeded.json"
OUT_DIR = Path("graph_visuals")
OUT_FILE = OUT_DIR / "ontology_hierarchy_graph.html"

HEIGHT = "900px"
WIDTH = "100%"
# --------------------------------------

OUT_DIR.mkdir(parents=True, exist_ok=True)

with open(ONTOLOGY_PATH, "r", encoding="utf-8") as f:
    ontology = json.load(f)

net = Network(
    height=HEIGHT,
    width=WIDTH,
    directed=True,
    notebook=False,
    bgcolor="#ffffff"
)

# ---------------- VIS OPTIONS ----------------
net.set_options("""
var options = {
  "nodes": {
    "shape": "ellipse",
    "font": { "size": 14 },
    "scaling": { "min": 18, "max": 36 }
  },
  "edges": {
    "arrows": { "to": { "enabled": true } },
    "font": { "size": 11, "align": "middle" }
  },
  "physics": {
    "hierarchicalRepulsion": {
      "centralGravity": 0.0,
      "springLength": 140,
      "springConstant": 0.01,
      "nodeDistance": 160
    },
    "solver": "hierarchicalRepulsion"
  }
}
""")

# ---------------- COLORS ----------------
CLASS_COLOR = "#4C78A8"
ISA_COLOR = "#E45756"
REL_COLOR = "#54A24B"

# ---------------- ADD CLASS NODES ----------------
for cls in ontology["classes"]:
    net.add_node(
        cls,
        label=cls,
        title=f"Ontology Class: {cls}",
        color=CLASS_COLOR,
        size=28
    )

# ---------------- ADD SUBCLASS EDGES (HIERARCHY) ----------------
for sc in ontology.get("subclasses", []):
    net.add_edge(
        sc["parent"],
        sc["child"],
        label="is_a",
        title=f'{sc["child"]} is a {sc["parent"]}',
        color=ISA_COLOR,
        width=3
    )

# ---------------- ADD OBJECT PROPERTIES ----------------
for rel, info in ontology.get("object_properties", {}).items():
    for domain in info.get("domain", []):
        for rng in info.get("range", []):
            net.add_edge(
                domain,
                rng,
                label=rel,
                title=f"{domain} → {rel} → {rng}",
                color=REL_COLOR,
                width=2,
                dashes=True
            )

# ---------------- LEGEND ----------------
legend_x = -900
legend_y = -450
step = 90

legend_items = [
    ("Class", CLASS_COLOR),
    ("Subclass (is_a)", ISA_COLOR),
    ("Object Property", REL_COLOR)
]

for i, (label, color) in enumerate(legend_items):
    net.add_node(
        f"legend_{label}",
        label=label,
        x=legend_x,
        y=legend_y + i * step,
        fixed=True,
        shape="box",
        color=color,
        physics=False
    )

# ---------------- SAVE ----------------
net.write_html(str(OUT_FILE), open_browser=False)
print(f"[OK] Ontology hierarchy graph written to {OUT_FILE}")
