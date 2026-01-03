from graph_vis_utils import *
import json
import networkx as nx

"""
REQUIRED INPUT (produced by your GraphRAG query pipeline):

query_traces/<query_id>.json

Example structure:
{
  "query": "...",
  "seed_nodes": ["node1", "node2"],
  "expanded_nodes": ["node3"],
  "used_edges": [["node1","node3"], ["node3","node2"]],
  "answer_nodes": ["node2"]
}
"""

QUERY_ID = "q_001"  # change as needed

with open(f"query_traces/{QUERY_ID}.json") as f:
    trace = json.load(f)

g = load_graph()
out = timestamp_dir()

nodes = set(trace["seed_nodes"]) | set(trace["expanded_nodes"]) | set(trace["answer_nodes"])
edges = [tuple(e) for e in trace["used_edges"]]

net = make_net(f"GraphRAG Query Trace – {QUERY_ID}")

for n in nodes:
    role = (
        "ANSWER" if n in trace["answer_nodes"]
        else "SEED" if n in trace["seed_nodes"]
        else "EXPANDED"
    )

    color = {
        "SEED": "#1f77b4",
        "EXPANDED": "#ff7f0e",
        "ANSWER": "#2ca02c",
    }[role]

    net.add_node(
        n,
        label=g.nodes[n].get("name", n),
        color=color,
        title=f"{role} NODE",
    )

for u, v in edges:
    net.add_edge(u, v, color="#000000")

# Manual legend (semantic)
net.add_node("LEG_SEED", label="Seed Node", color="#1f77b4", shape="box", physics=False)
net.add_node("LEG_EXP", label="Expanded Node", color="#ff7f0e", shape="box", physics=False)
net.add_node("LEG_ANS", label="Answer Node", color="#2ca02c", shape="box", physics=False)
ts = datetime.now().strftime("%Y-%m-%d_%H-%M")
path = out / f"query_trace_{QUERY_ID}_{ts}.html"
save_html(net,str(path))
print("✅ Query trace graph saved:", path)
