from graph_store import GraphStore

s = GraphStore()
s.load()

print("Nodes:", s.graph.number_of_nodes())
print("Edges:", s.graph.number_of_edges())
