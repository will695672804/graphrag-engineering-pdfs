# graph_store.py
import os
import networkx as nx
#from networkx.readwrite.gpickle import write_gpickle, read_gpickle
import pickle
from pathlib import Path
from config import INDEX_DIR
from canonicalizer import canonicalize
from extraction_mode import ExtractionMode
class GraphStore:
    def __init__(self):
        self.graph = nx.MultiDiGraph()

    def add_entities(self, entities):
        id_map = {}

        for e in entities:
            eid = e["id"]

            # 🔴 DO NOT DROP during bootstrap
            if eid not in self.graph:
                self.graph.add_node(
                    eid,
                    **e
                )

            id_map[eid] = eid

        return id_map

    def add_relations(self, relations, id_map):
        for r in relations:
            src = id_map.get(r["source"])
            tgt = id_map.get(r["target"])

            if not src or not tgt:
                continue  # Skip dangling relations safely

            self.graph.add_edge(
                src,
                tgt,
                type=r["type"],
                evidence=r.get("evidence")
            )

    def save(self):
        Path(INDEX_DIR).mkdir(exist_ok=True)
        graph_path = os.path.join(INDEX_DIR, "graph.pkl")

        with open(graph_path, "wb") as f:
            pickle.dump(self.graph, f, protocol=pickle.HIGHEST_PROTOCOL)

        print(f"💾 Graph saved → {graph_path}")

    def load(self):
        graph_path = os.path.join(INDEX_DIR, "graph.pkl")

        if not os.path.exists(graph_path):
            raise FileNotFoundError(
                f"Graph file not found at {graph_path}. "
                "Run index_documents.py first."
            )

        with open(graph_path, "rb") as f:
            self.graph = pickle.load(f)

        if not isinstance(self.graph, nx.Graph):
            raise TypeError(
                f"Loaded object is not a NetworkX graph: {type(self.graph)}"
            )

        print(f"📥 Graph loaded → {graph_path}")
