# detect_graph_misses.py
import json
from graphrag_query import (
    vector_only_answer,
    graph_only_answer,
    vector_retrieve,
    load_vector_index,
)

QUESTIONS = [
    "What operating sequence applies to 245 kV SF6 circuit breakers?",
    "What causes insulation failure in power transformers?",
    "Which maintenance actions mitigate SF6 leakage?"
]

OUTPUT_FILE = "index/missed_knowledge.json"


def detect_graph_misses():
    index, chunks = load_vector_index()
    misses = []

    for q in QUESTIONS:
        graph_ans = graph_only_answer(q)
        vector_ans = vector_only_answer(q)

        # Heuristic: graph failed, vector succeeded
        if "no information" in graph_ans.lower():
            context = vector_retrieve(index, chunks, q, top_k=3)

            misses.append({
                "question": q,
                "graph_answer": graph_ans,
                "vector_answer": vector_ans,
                "supporting_chunks": context
            })

            print(f"❌ Graph miss detected: {q}")
        else:
            print(f"✅ Graph covered: {q}")

    with open(OUTPUT_FILE, "w") as f:
        json.dump(misses, f, indent=2)

    print(f"\n📌 Missed knowledge written to {OUTPUT_FILE}")


if __name__ == "__main__":
    detect_graph_misses()
