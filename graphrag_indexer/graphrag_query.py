# graphrag_query.py
import json
import pickle
from sentence_transformers import SentenceTransformer
from llm_client import call_llm
try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False


from config import INDEX_DIR

EMBED_MODEL = SentenceTransformer("all-MiniLM-L6-v2")

# -----------------------------
# Loaders
# -----------------------------

def load_graph():
    with open(f"{INDEX_DIR}/graph.pkl", "rb") as f:
        return pickle.load(f)

def load_vector_index():
    index = faiss.read_index(f"{INDEX_DIR}/faiss.index")
    with open(f"{INDEX_DIR}/vector_chunks.pkl", "rb") as f:
        chunks = pickle.load(f)
    return index, chunks

def load_communities():
    try:
        with open(f"{INDEX_DIR}/communities.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return None


# -----------------------------
# Community selection
# -----------------------------

def select_communities(graph, communities, query_terms):
    """
    Return a set of community IDs relevant to the query
    """
    selected = set()

    for node, data in graph.nodes(data=True):
        name = data.get("name", "").lower()
        if any(t in name for t in query_terms):
            if node in communities:
                selected.add(communities[node])

    return selected


# -----------------------------
# Graph retrieval (community-aware)
# -----------------------------

def graph_retrieve(graph, communities, query_terms):
    facts = []

    if communities:
        relevant_cids = select_communities(graph, communities, query_terms)
    else:
        relevant_cids = None  # fallback

    for u, v, ed in graph.edges(data=True):
        if communities and relevant_cids is not None:
            if communities.get(u) not in relevant_cids:
                continue

        facts.append({
            "source": u,
            "target": v,
            "type": ed.get("type"),
            "evidence": ed.get("evidence"),
            "pages": ed.get("page") or ed.get("pages")
        })

    return facts


# -----------------------------
# Vector retrieval
# -----------------------------

def vector_retrieve(index, chunks, question, top_k=5):
    q_emb = EMBED_MODEL.encode([question])
    _, ids = index.search(q_emb, top_k)

    return [chunks[i] for i in ids[0]]


# -----------------------------
# Hybrid Answer (Community-aware)
# -----------------------------

def hybrid_answer_community_aware(question):
    graph = load_graph()
    v_index, v_chunks = load_vector_index()
    communities = load_communities()

    query_terms = question.lower().split()

    graph_facts = graph_retrieve(graph, communities, query_terms)
    vector_context = vector_retrieve(v_index, v_chunks, question)

    prompt = f"""
You are a senior power-systems engineer.

RULES:
- Use GRAPH FACTS as the source of truth
- Use VECTOR CONTEXT only for explanation and completeness
- Prefer facts from the same COMMUNITY
- Cite chapter/section/pages where available
- Do not hallucinate missing parameters

GRAPH FACTS:
{graph_facts}

VECTOR CONTEXT:
{vector_context}

QUESTION:
{question}

ANSWER:
"""

    return call_llm(prompt)
# ============================================================
# Retrieval Strategies
# ============================================================

def vector_only_answer(question):
    index, chunks = load_vector_index()
    context = vector_retrieve(index, chunks, question, top_k=5)

    prompt = f"""
Answer the question using ONLY the provided context.
If the answer is missing, say so.

CONTEXT:
{context}

QUESTION:
{question}

ANSWER:
"""
    return call_llm(prompt)


def graph_only_answer(question):
    graph = load_graph()
    facts = graph_retrieve(
        graph,
        communities=None,
        query_terms=question.lower().split()
    )

    prompt = f"""
Answer using ONLY the structured facts below.
Do not add external knowledge.

FACTS:
{facts}

QUESTION:
{question}

ANSWER:
"""
    return call_llm(prompt)


def hybrid_answer(question):
    graph = load_graph()
    index, chunks = load_vector_index()

    facts = graph_retrieve(
        graph,
        communities=None,
        query_terms=question.lower().split()
    )
    context = vector_retrieve(index, chunks, question, top_k=5)

    prompt = f"""
Use GRAPH FACTS as authoritative truth.
Use VECTOR CONTEXT only for explanation.

GRAPH FACTS:
{facts}

VECTOR CONTEXT:
{context}

QUESTION:
{question}

ANSWER:
"""
    return call_llm(prompt)


def hybrid_answer_with_communities(question):
    graph = load_graph()
    index, chunks = load_vector_index()
    communities = load_communities()

    facts = graph_retrieve(
        graph,
        communities=communities,
        query_terms=question.lower().split()
    )
    context = vector_retrieve(index, chunks, question, top_k=5)

    prompt = f"""
You are a domain expert.

RULES:
- Prefer GRAPH FACTS from the same COMMUNITY
- Use VECTOR CONTEXT only to explain
- Do not mix unrelated equipment

GRAPH FACTS:
{facts}

VECTOR CONTEXT:
{context}

QUESTION:
{question}

ANSWER:
"""
    return call_llm(prompt)
