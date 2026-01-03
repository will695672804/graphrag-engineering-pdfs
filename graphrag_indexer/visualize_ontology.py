import json
from pathlib import Path
from pyvis.network import Network

# ---------------- CONFIG ----------------
ONTOLOGY_PATH = "index/ontology.json"
OUT_DIR = Path("graph_visuals")
OUT_FILE = OUT_DIR / "ontology_graph.html"

MAX_INSTANCES_PER_CLASS = 8
HEIGHT = "900px"
WIDTH = "100%"
# ---------------------------------------

OUT_DIR.mkdir(parents=True, exist_ok=True)

with open(ONTOLOGY_PATH, "r", encoding="utf-8") as f:
    ontology = json.load(f)

net = Network(
    height=HEIGHT,
    width=WIDTH,
    directed=True,
    notebook=False
)

# ---------------- VIS OPTIONS ----------------
net.set_options("""
var options = {
  "nodes": {
    "font": { "size": 14 },
    "scaling": { "min": 10, "max": 30 }
  },
  "edges": {
    "arrows": { "to": { "enabled": true } },
    "font": { "size": 11, "align": "middle" }
  },
  "physics": {
    "forceAtlas2Based": {
      "gravitationalConstant": -60,
      "springLength": 120,
      "springConstant": 0.05
    },
    "solver": "forceAtlas2Based",
    "stabilization": { "iterations": 250 }
  }
}
""")

# ---------------- COLORS ----------------
CLASS_COLOR = "#4C78A8"
INSTANCE_COLOR = "#F58518"
PROPERTY_COLOR = "#54A24B"

# ---------------- ADD CLASSES ----------------
for cls in ontology["classes"]:
    net.add_node(
        cls,
        label=cls,
        shape="ellipse",
        color=CLASS_COLOR,
        size=28,
        title=f"Class: {cls}"
    )

# ---------------- ADD OBJECT PROPERTIES ----------------
for rel, info in ontology["object_properties"].items():
    for domain in info["domain"]:
        for rng in info["range"]:
            net.add_edge(
                domain,
                rng,
                label=rel,
                title=f"{domain} → {rel} → {rng}",
                color=PROPERTY_COLOR,
                width=2
            )

# ---------------- ADD INSTANCES (SAMPLED) ----------------
for cls, insts in ontology["instances"].items():
    for inst in insts[:MAX_INSTANCES_PER_CLASS]:
        inst_id = f"{cls}:{inst}"

        net.add_node(
            inst_id,
            label=inst,
            shape="dot",
            color=INSTANCE_COLOR,
            size=10,
            title=f"Instance of {cls}"
        )

        net.add_edge(
            inst_id,
            cls,
            label="instance_of",
            color="#999999",
            dashes=True
        )

# ---------------- ADD LEGEND ----------------
legend_x = -800
legend_y = -400
step = 80

legend_items = [
    ("Class", CLASS_COLOR),
    ("Instance", INSTANCE_COLOR),
    ("Object Property", PROPERTY_COLOR)
]

for i, (label, color) in enumerate(legend_items):
    node_id = f"legend_{label}"
    net.add_node(
        node_id,
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

print(f"[OK] Ontology visualization written to {OUT_FILE}")
