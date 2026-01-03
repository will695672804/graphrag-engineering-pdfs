def graph_coverage(G):
    by_type = {}
    for _, d in G.nodes(data=True):
        t = d.get("type", "Unknown")
        by_type[t] = by_type.get(t, 0) + 1
    return by_type

def orphan_nodes(G):
    return [n for n in G.nodes() if G.degree(n) == 0]
