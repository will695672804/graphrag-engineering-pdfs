# visualize_graph.py
#
# Safe visualization for large GraphRAG graphs
# - Works with graph.pkl
# - Samples nodes if graph is large
# - Optional: visualize core graph or a single community

import pickle
import random
from pathlib import Path

import networkx as nx
import matplotlib.pyplot as plt

INDEX_DIR = "index"
GRAPH_PATH = Path(INDEX_DIR) / "graph.pkl"

# -------------------------------
# CONFIG
# -------------------------------
MAX_NODES = 300        # hard cap for plotting
MIN_DEGREE = 2         # filter weak nodes
LAYOUT = "spring"      # spring | kamada_kawai

# -------------------------------
# LOAD GRAPH
# -------------------------------
with open(GRAPH_PATH, "rb") as f:
    graph = pickle.load(f)

print(f"📥 Graph loaded")
print(f"   Nodes: {graph.number_of_nodes()}")
print(f"   Edges: {graph.number_of_edges()}")

# -------------------------------
# FILTER CORE GRAPH
# -------------------------------
core_nodes = [
    n for n in graph.nodes()
    if graph.degree(n) >= MIN_DEGREE
]

core_graph = graph.subgraph(core_nodes).copy()

print(f"🧠 Core graph (degree ≥ {MIN_DEGREE})")
print(f"   Nodes: {core_graph.number_of_nodes()}")
print(f"   Edges: {core_graph.number_of_edges()}")

# -------------------------------
# SAMPLE IF TOO LARGE
# -------------------------------
if core_graph.number_of_nodes() > MAX_NODES:
    sampled_nodes = random.sample(
        list(core_graph.nodes()), MAX_NODES
    )
    vis_graph = core_graph.subgraph(sampled_nodes).copy()
    print(f"✂️ Sampled graph to {MAX_NODES} nodes")
else:
    vis_graph = core_graph

# -------------------------------
# NODE COLORS BY TYPE
# -------------------------------
def node_color(n):
    t = vis_graph.nodes[n].get("type", "")
    return {
        "Equipment": "#1f77b4",
        "Component": "#ff7f0e",
        "Parameter": "#2ca02c",
        "MaintenanceAction": "#d62728",
        "FailureMode": "#9467bd",
        "Standard": "#8c564b",
    }.get(t, "#7f7f7f")


colors = [node_color(n) for n in vis_graph.nodes()]

# -------------------------------
# LAYOUT
# -------------------------------
if LAYOUT == "kamada_kawai":
    pos = nx.kamada_kawai_layout(vis_graph)
else:
    pos = nx.spring_layout(vis_graph, k=0.4, seed=42)

# -------------------------------
# DRAW
# -------------------------------
plt.figure(figsize=(16, 14))
nx.draw_networkx_nodes(
    vis_graph,
    pos,
    node_color=colors,
    node_size=300,
    alpha=0.85,
)
nx.draw_networkx_edges(
    vis_graph,
    pos,
    width=0.5,
    alpha=0.4,
)
nx.draw_networkx_labels(
    vis_graph,
    pos,
    font_size=7,
)

plt.title("GraphRAG Knowledge Graph (Core View)", fontsize=16)
plt.axis("off")
plt.tight_layout()
plt.show()
