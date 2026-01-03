from graph_vis_utils import *
import networkx as nx

g = load_graph()
out = timestamp_dir()

communities = list(nx.algorithms.community.greedy_modularity_communities(g))
largest = max(communities, key=len)
sub = g.subgraph(largest)

net = make_net(f"Largest Community ({len(sub)} nodes)")

for n in sub.nodes():
    net.add_node(
        n,
        label=g.nodes[n].get("name", n),
        color=node_color(n, g),
        title=str(g.nodes[n]),
    )

for u, v, d in sub.edges(data=True):
    net.add_edge(u, v, label=d.get("type", ""))

add_legend(net)
ts = datetime.now().strftime("%Y-%m-%d_%H-%M")
path = out / f"largest_community_{ts}.html"
save_html(net,str(path))
print(f"✅ Saved: {path}")
