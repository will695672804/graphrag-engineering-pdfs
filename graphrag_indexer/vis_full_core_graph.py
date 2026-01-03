from graph_vis_utils import *

g = load_graph()
out = timestamp_dir()

MIN_DEGREE = 2
MAX_NODES = 400

core_nodes = [n for n in g if g.degree(n) >= MIN_DEGREE]
core = g.subgraph(core_nodes)

if core.number_of_nodes() > MAX_NODES:
    core = core.subgraph(list(core.nodes())[:MAX_NODES])

net = make_net("GraphRAG – Core Knowledge Graph")

for n in core.nodes():
    net.add_node(
        n,
        label=g.nodes[n].get("name", n),
        color=node_color(n, g),
        title=str(g.nodes[n]),
    )

for u, v, d in core.edges(data=True):
    net.add_edge(u, v, label=d.get("type", ""))

add_legend(net)
ts = datetime.now().strftime("%Y-%m-%d_%H-%M")
path = out / f"full_core_graph_{ts}.html"
save_html(net, str(path))
print(f"✅ Saved: {path}")
