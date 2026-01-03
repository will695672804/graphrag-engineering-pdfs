# evaluate_queries.py
from graphrag_query import hybrid_answer_community_aware
from llm_client import call_llm
import json

TEST_QUESTIONS = [
    "What operating sequence applies to 245 kV SF6 circuit breakers?",
    "What causes insulation failure in power transformers?",
    "Which maintenance actions mitigate SF6 leakage?"
]


def graph_only_answer(question):
    prompt = f"""
Answer using ONLY structured graph facts.
Do not add explanations.

Question:
{question}
"""
    return call_llm(prompt)


def run_evaluation():
    results = []

    for q in TEST_QUESTIONS:
        g_ans = graph_only_answer(q)
        h_ans = hybrid_answer_community_aware(q)

        results.append({
            "question": q,
            "graph_only": g_ans,
            "hybrid": h_ans
        })

    with open("index/evaluation.json", "w") as f:
        json.dump(results, f, indent=2)

    print("✅ Evaluation complete")


if __name__ == "__main__":
    run_evaluation()
