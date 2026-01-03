# build_communities_only.py
import pickle, json
from community_detection import detect_communities

INDEX_DIR = "index"

with open(f"{INDEX_DIR}/graph.pkl", "rb") as f:
    graph = pickle.load(f)

print("🧠 Detecting communities...")
communities = detect_communities(graph)

with open(f"{INDEX_DIR}/communities.json", "w") as f:
    json.dump(communities, f, indent=2)

print("✅ communities.json written")
