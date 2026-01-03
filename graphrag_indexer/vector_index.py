from sentence_transformers import SentenceTransformer
import faiss
import pickle
from pathlib import Path

model = SentenceTransformer("all-MiniLM-L6-v2")

def build_vector_index(chunks):
    Path("index").mkdir(parents=True, exist_ok=True)

    if not chunks:
        raise ValueError("❌ No chunks provided to build_vector_index")

    texts = [c.get("text", "").strip() for c in chunks]
    texts = [t for t in texts if t]

    if not texts:
        raise ValueError("❌ All chunks have empty text. Cannot build vector index.")

    embeddings = model.encode(texts)

    # --- SAFETY CHECK ---
    if len(embeddings.shape) != 2 or embeddings.shape[0] == 0:
        raise ValueError(
            f"❌ Invalid embeddings shape: {embeddings.shape}"
        )

    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(embeddings)

    with open("index/vector_chunks.pkl", "wb") as f:
        pickle.dump(chunks, f)

    faiss.write_index(index, "index/faiss.index")

    print(
        f"✅ Vector index built: "
        f"{embeddings.shape[0]} vectors, dim={dim}"
    )

# -------------------------------
# Vector search + lookup helpers
# -------------------------------

def load_vector_index():
    index = faiss.read_index("index/faiss.index")
    with open("index/vector_chunks.pkl", "rb") as f:
        chunks = pickle.load(f)
    return index, chunks


def vector_search(query: str, top_k: int = 5):
    """
    Returns list of dicts:
    [{ "chunk_id": int, "score": float }]
    """
    index, chunks = load_vector_index()

    q_emb = model.encode([query])
    scores, ids = index.search(q_emb, top_k)

    results = []
    for i, score in zip(ids[0], scores[0]):
        if i < 0 or i >= len(chunks):
            continue
        results.append({
            "chunk_id": i,
            "score": float(score)
        })
    return results


def get_chunk_lookup():
    """
    Returns:
    { chunk_id -> chunk_dict }
    """
    _, chunks = load_vector_index()
    return {i: c for i, c in enumerate(chunks)}
