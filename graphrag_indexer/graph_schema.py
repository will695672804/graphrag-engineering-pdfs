# graph_schema.py
import pickle
from collections import Counter

GRAPH_FILE = "index/graph.pkl"


def load_graph():
    with open(GRAPH_FILE, "rb") as f:
        return pickle.load(f)


def extract_schema():
    graph = load_graph()

    entity_types = Counter()
    relation_types = Counter()

    for _, data in graph.nodes(data=True):
        if "type" in data:
            entity_types[data["type"]] += 1

    for _, _, data in graph.edges(data=True):
        if "type" in data:
            relation_types[data["type"]] += 1

    return {
        "entity_types": dict(entity_types),
        "relation_types": dict(relation_types),
    }



if __name__ == "__main__":
    schema = extract_schema()
    print(schema)
