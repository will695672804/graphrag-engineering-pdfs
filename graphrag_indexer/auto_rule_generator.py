# auto_rule_generator.py
from graph_schema import extract_schema
import json
import re
from extractor import call_llm

MISSES_FILE = "index/missed_knowledge.json"
OUTPUT_RULES = "index/suggested_extractor_rules.json"

schema = extract_schema()

PROMPT = """
You are improving a technical knowledge extractor.

The CURRENT GRAPH contains:

ENTITY TYPES:
{entity_types}

RELATION TYPES:
{relation_types}

Given a MISSED FACT and SOURCE TEXT:

1. Decide whether the fact maps to an EXISTING relation type.
2. If yes:
   - return that relation name
   - list synonyms to normalize
3. If no:
   - propose ONE new relation type
   - explain why it is needed

⚠️ IMPORTANT:
Return ONLY valid JSON. No explanation text.

JSON SCHEMA:
{{
  "mapped_relation": "string",
  "is_new_relation": true_or_false,
  "synonyms": ["string"],
  "regex": "string or null"
}}

MISSED FACT:
{question}

SOURCE TEXT:
{chunk}
"""


def extract_json(text):
    """Safely extract first JSON object from LLM output."""
    match = re.search(r"\{[\s\S]*\}", text)
    if not match:
        return None
    try:
        return json.loads(match.group(0))
    except Exception:
        return None


def flatten_chunks(chunks):
    """Convert list of chunk dicts into readable text."""
    texts = []
    for c in chunks:
        texts.append(
            f"[Chapter: {c.get('chapter')} | Section: {c.get('section')}]\n{c.get('text')}"
        )
    return "\n\n".join(texts)


def generate_rules():
    misses = json.load(open(MISSES_FILE))
    rules = []

    for m in misses:
        chunk_text = flatten_chunks(m["supporting_chunks"])

        prompt = PROMPT.format(
            entity_types=list(schema["entity_types"].keys()),
            relation_types=list(schema["relation_types"].keys()),
            question=m["question"],
            chunk=chunk_text
        )

        response = call_llm(prompt)
        rule = extract_json(response)

        if rule:
            rules.append(rule)
        else:
            print("⚠️ LLM response was not valid JSON")

    with open(OUTPUT_RULES, "w") as f:
        json.dump(rules, f, indent=2)

    print(f"🧠 Suggested rules written to {OUTPUT_RULES}")


if __name__ == "__main__":
    generate_rules()
