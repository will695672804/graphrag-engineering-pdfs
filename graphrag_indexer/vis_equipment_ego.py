from graph_vis_utils import *
import networkx as nx

TARGET_TYPE = "Equipment"
RADIUS = 1

g = load_graph()
out = timestamp_dir()

equipment = next(
    n for n, d in g.nodes(data=True)
    if d.get("type") == TARGET_TYPE
)

ego = nx.ego_graph(g, equipment, radius=RADIUS)

net = make_net(f"Ego Graph – {g.nodes[equipment].get('name')}")

for n in ego.nodes():
    net.add_node(
        n,
        label=g.nodes[n].get("name", n),
        color=node_color(n, g),
        title=str(g.nodes[n]),
    )

for u, v, d in ego.edges(data=True):
    net.add_edge(u, v, label=d.get("type", ""))

add_legend(net)

path = out / "equipment_ego_graph.html"
net.show(str(path))
print(f"✅ Saved: {path}")
