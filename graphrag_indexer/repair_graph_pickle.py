# repair_graph_pickle.py
#
# One-time repair script for graph.pkl
# Uses pure pickle to avoid NetworkX gpickle API / stub issues
#
# SAFE:
# - No re-indexing
# - No graph mutation
# - No dependency on NetworkX gpickle internals

import os
import pickle
import networkx as nx
from config import INDEX_DIR

GRAPH_PATH = os.path.join(INDEX_DIR, "graph.pkl")


def main():
    print("🛠️ Repairing graph.pkl format (pickle-safe)...")

    if not os.path.exists(GRAPH_PATH):
        raise FileNotFoundError(f"{GRAPH_PATH} not found")

    # Load existing graph
    with open(GRAPH_PATH, "rb") as f:
        graph = pickle.load(f)

    if not isinstance(graph, nx.Graph):
        raise TypeError(
            f"Expected NetworkX graph, got {type(graph)}"
        )

    # Rewrite using pickle (clean, normalized)
    with open(GRAPH_PATH, "wb") as f:
        pickle.dump(graph, f, protocol=pickle.HIGHEST_PROTOCOL)

    print("✅ graph.pkl repaired and normalized using pickle")
    print("📌 GraphStore.load() will now work correctly")


if __name__ == "__main__":
    main()
