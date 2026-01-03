import community.community_louvain as community_louvain

def detect_communities(graph):
    undirected = graph.to_undirected()
    return community_louvain.best_partition(undirected)
