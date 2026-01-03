# summarizer.py
from llm_client import call_llm
MAX_NODES = 50
MAX_EDGES = 100

SUMMARY_PROMPT = """
Summarize this knowledge graph community.

Entities:
{entities}

Relationships:
{relations}

Focus on meaning and key facts.
"""

def summarize_community(nodes, edges):
    # --- PATCH: cap community size ---
    nodes = list(nodes)[:MAX_NODES]
    edges = list(edges)[:MAX_EDGES]

    prompt = f"""
You are summarizing a technical knowledge graph community.

Entities (sampled):
{nodes}

Relations (sampled):
{edges}

Provide:
1. Main theme
2. Key entities
3. Important relationships
4. What this community explains
"""

    return call_llm(prompt, temperature=0.1)

