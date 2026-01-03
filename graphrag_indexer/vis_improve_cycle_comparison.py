from graph_vis_utils import *
import json

# REQUIRED FILES
# index/graph_bootstrap.pkl  ← graph before improve cycle
# index/graph.pkl            ← final improved graph

g_before = load_graph("index/graph_bootstrap.pkl")
g_after  = load_graph("index/graph.pkl")

out = timestamp_dir()

nodes_before = set(g_before.nodes())
nodes_after  = set(g_after.nodes())
edges_before = set(g_before.edges())
edges_after  = set(g_after.edges())

new_nodes = nodes_after - nodes_before
new_edges = edges_after - edges_before

metrics = {
    "nodes_before": len(nodes_before),
    "nodes_after": len(nodes_after),
    "new_nodes": len(new_nodes),
    "edges_before": len(edges_before),
    "edges_after": len(edges_after),
    "new_edges": len(new_edges),
}

with open(out / "improve_metrics.json", "w") as f:
    json.dump(metrics, f, indent=2)

net = make_net("Before vs After Improve-Cycle (Green = New)")

for n in nodes_after:
    is_new = n in new_nodes
    net.add_node(
        n,
        label=g_after.nodes[n].get("name", n),
        color="#2ca02c" if is_new else node_color(n, g_after),
        title=f"NEW NODE" if is_new else "Existing",
    )

for u, v in edges_after:
    net.add_edge(
        u,
        v,
        color="#2ca02c" if (u, v) in new_edges else "#999999",
    )

add_legend(net)
ts = datetime.now().strftime("%Y-%m-%d_%H-%M")
path = out / f"improve_cycle_comparison_{ts}.html"
save_html(net,str(path))
print("✅ Improve-cycle comparison saved:", path)
print("📊 Metrics:", metrics)
