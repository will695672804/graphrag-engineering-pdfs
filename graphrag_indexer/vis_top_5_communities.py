from graph_vis_utils import *
import networkx as nx
import itertools

g = load_graph()
out = timestamp_dir()

communities = sorted(
    nx.algorithms.community.greedy_modularity_communities(g),
    key=len,
    reverse=True
)[:5]

palette = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd"]
net = make_net("Top 5 Communities")

for idx, comm in enumerate(communities):
    for n in comm:
        net.add_node(
            n,
            label=g.nodes[n].get("name", n),
            color=palette[idx],
            title=f"Community {idx+1}",
        )

for comm in communities:
    for u, v in g.subgraph(comm).edges():
        net.add_edge(u, v)

add_legend(net)
ts = datetime.now().strftime("%Y-%m-%d_%H-%M")
path = out / f"top_5_communities_{ts}.html"
save_html(net,str(path))
print(f"✅ Saved: {path}")
