# graph_vis_utils.py

import pickle
from pathlib import Path
from datetime import datetime
from pyvis.network import Network

COLOR_MAP = {
    "Equipment": "#1f77b4",
    "Component": "#ff7f0e",
    "Parameter": "#2ca02c",
    "MaintenanceAction": "#d62728",
    "FailureMode": "#9467bd",
    "Standard": "#8c564b",
}

def timestamp_dir(base="graph_visuals"):
    #ts = datetime.now().strftime("%Y-%m-%d_%H-%M")
    out = Path(base) #/ ts
    out.mkdir(parents=True, exist_ok=True)
    return out

def load_graph():
    with open("index/graph.pkl", "rb") as f:
        return pickle.load(f)

def make_net(title):
    net = Network(
        height="800px",
        width="100%",
        bgcolor="#ffffff",
        font_color="black",
        notebook=False,
        directed=True,
    )
    net.heading = title
    net.toggle_physics(True)
    return net

def add_legend(net):
    for label, color in COLOR_MAP.items():
        net.add_node(
            f"LEGEND_{label}",
            label=label,
            color=color,
            shape="box",
            physics=False,
        )

def node_color(n, g):
    return COLOR_MAP.get(g.nodes[n].get("type", ""), "#7f7f7f")
def save_html(net, path):
    net.write_html(str(path), open_browser=False)
    print(f"✅ Graph saved → {path}")

