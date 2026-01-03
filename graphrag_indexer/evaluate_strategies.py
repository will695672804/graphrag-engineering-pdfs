import json
from graphrag_query import (
    hybrid_answer,
    hybrid_answer_with_communities,
    graph_only_answer,
    vector_only_answer,
)

QUESTIONS = [
    # Circuit Breakers & Switchgear
    "What is the rated operating sequence (duty cycle) for 245 kV SF6 circuit breakers?",
    "What total break time limits are specified for 420 kV and 800 kV circuit breakers?",
    "Which operating mechanisms are permitted for EHV circuit breakers?",
    "What are the standard voltage levels at which SF6 circuit breakers are used in India?",
    "What conditions differentiate auto-reclosure duty cycles from non-auto-reclosure duty cycles?",

    # Disconnectors, Earthing & Switching
    "What functional role do disconnect switches serve in EHV substations?",
    "How does the physical placement of disconnect switches affect maintenance effort?",
    "What is the primary function of an earthing switch in a substation?",
    "Which types of disconnect switches are used at 420 kV and 800 kV voltage levels?",
    "Why are disconnect switches not intended to interrupt load current?",

    # Instrument Transformers
    "What are the differences between bushing type and wound type current transformers?",
    "Where are voltage transformers typically located relative to circuit breakers?",
    "Why are capacitor voltage transformers preferred at voltages above 132 kV?",
    "What is the purpose of an open-delta winding in voltage transformers?",
    "What insulation levels are specified for current transformers at 400 kV?",

    # Power Transformers
    "What are the main causes of insulation failure in power transformers?",
    "How does ONAN cooling differ from ONAF and ODAF cooling methods?",
    "What transformer vector groups are specified for 220 kV and 400 kV substations?",
    "Why is residual life assessment important for EHV power transformers?",
    "What installation constraints influence transformer bay layout in EHV substations?",

    # Lightning Protection & Insulation
    "How are substations protected against direct lightning strokes?",
    "What factors determine the placement of surge arresters in EHV substations?",
    "Why are switching over-voltages a concern at EHV voltage levels?",
    "How does pollution level influence required creepage distance for insulators?",
    "What mitigation methods are recommended for heavily polluted substation environments?",

    # Protection & Maintenance Philosophy
    "What protection schemes are recommended for 400 kV transmission lines?",
    "What protective devices are mandatory for 220 kV and 400 kV power transformers?",
    "What is the role of local breaker backup (LBB) protection?",
    "Why is condition-based maintenance preferred over breakdown maintenance?"
]



def run_evaluation():
    results = []

    for q in QUESTIONS:
        print(f"\n🔍 Evaluating: {q}")

        results.append({
            "question": q,
            "vector_only": vector_only_answer(q),
            "graph_only": graph_only_answer(q),
            "hybrid_no_communities": hybrid_answer(q),
            "hybrid_with_communities": hybrid_answer_with_communities(q),
        })

    with open("index/strategy_comparison.json", "w") as f:
        json.dump(results, f, indent=2)

    print("\n✅ Strategy comparison saved → index/strategy_comparison.json")


if __name__ == "__main__":
    run_evaluation()
