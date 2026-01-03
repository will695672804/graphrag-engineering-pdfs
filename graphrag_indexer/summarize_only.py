if __name__ == "__main__":
    from graph_store import GraphStore
    from community_detection import detect_communities
    from summarizer import summarize_community
    import json
    store = GraphStore()
    store.load()

    graph = store.graph
    print("🧠 Rebuilding communities (no re-index)...")
    communities = detect_communities(graph)

    summaries = {}
    from collections import defaultdict

    # 🔁 Normalize community structure
    community_nodes = defaultdict(list)

    for node, cid in communities.items():
        community_nodes[cid].append(node)

    print(f"🧠 Total communities: {len(community_nodes)}")

    # 📊 Community size histogram (one-liner you asked for)
    print("📊 Community size histogram:",
          sorted(len(v) for v in community_nodes.values()))

    summaries = {}

    for cid, nodes in community_nodes.items():
        if len(nodes) < 2:
            continue  # skip trivial communities

        subg = graph.subgraph(nodes)
        edges = list(subg.edges(data=True))

        summaries[cid] = summarize_community(nodes, edges)

    with open("index/community_summaries.json", "w") as f:
        json.dump(summaries, f, indent=2)

    print("✅ Community summaries regenerated")
    from collections import Counter

    print("📊 Community size buckets:", Counter(len(v) // 10 * 10 for v in communities.values()))
