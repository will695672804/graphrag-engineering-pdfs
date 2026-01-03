# extractor.py

from llm_client import call_llm
from extraction_mode import ExtractionMode
from seed_schema import SEED_ENTITY_TYPES, SEED_RELATION_TYPES
from graph_schema import extract_schema
from domain_materializer import materialize_domain_facts
from canonical_observer import observe_entities, observe_relations, save_observations
EXTRACTION_MODE = ExtractionMode.IMPROVE  # default

import json
import os

SUGGESTED_RULES_FILE = "index/suggested_extractor_rules.json"

EXTRACTION_PROMPT = """
You are a senior power systems engineer building a TECHNICAL KNOWLEDGE GRAPH
from an engineering manual.

────────────────────────────────────────
EXTRACTION MODE: {mode}
────────────────────────────────────────

DOCUMENT CONTEXT:
- Chapter: {chapter}
- Section: {section}
- Subsection: {subsection}
- Pages: {pages}

Interpret the text STRICTLY in this document context.
Do NOT introduce information not grounded in the text.

────────────────────────────────────────
TASK
────────────────────────────────────────
Extract an EQUIPMENT-CENTRIC knowledge graph.

The graph must reflect how a practicing power systems engineer
would reason about equipment, operation, failure, and maintenance.

────────────────────────────────────────
GLOBAL RULES (APPLY IN ALL MODES)
────────────────────────────────────────
1. Prioritize PHYSICAL EQUIPMENT and ENGINEERED COMPONENTS.
2. Treat the following as FIRST-CLASS entities when present:
   - Ratings and limits (voltage, current, pressure, time)
   - Operating sequences and duty cycles
   - Failure mechanisms and causes
   - Maintenance and mitigation actions
   - Standards and compliance references
3. Prefer TECHNICAL, DOMAIN-SPECIFIC relationships over generic ones.
4. Infer IMPLICIT engineering relationships only when they are
   logically unavoidable to a domain expert.
5. Avoid vague abstractions unless explicitly tied to equipment.

────────────────────────────────────────
MODE-SPECIFIC BEHAVIOR
────────────────────────────────────────

IF MODE = BOOTSTRAP:
- You are building the FIRST version of the graph.
- Use ONLY the allowed ENTITY TYPES and RELATION TYPES listed below.
- Be PERMISSIVE in extraction:
  - If a fact is important but does not perfectly match a relation,
    choose the closest relation.
- Do NOT invent new relation types.
- It is acceptable if some relations are coarse-grained.

IF MODE = IMPROVE:
- You are IMPROVING an existing graph.
- STRONGLY prefer ALIGNMENT with existing relation types.
- Normalize equivalent concepts (e.g., “duty cycle” vs “operating sequence”).
- Only propose a NEW relation type if:
  - The fact is important, AND
  - No existing relation can represent it without loss of meaning.
- Be more PRECISE than in BOOTSTRAP mode.

────────────────────────────────────────
ALLOWED ENTITY TYPES
────────────────────────────────────────
{allowed_entity_types}

────────────────────────────────────────
ALLOWED RELATION TYPES
────────────────────────────────────────
{allowed_relation_types}

────────────────────────────────────────
OUTPUT REQUIREMENTS
────────────────────────────────────────
Return STRICT JSON ONLY.
Do NOT include explanations outside JSON.

Schema:
{{
  "entities": [
    {{
      "id": "string",
      "type": "one of ALLOWED ENTITY TYPES",
      "name": "canonical technical name"
    }}
  ],
  "relations": [
    {{
      "source": "entity_id",
      "target": "entity_id",
      "type": "one of ALLOWED RELATION TYPES",
      "evidence": "explicit quote or concise engineering rationale"
    }}
  ]
}}

────────────────────────────────────────
TEXT TO ANALYZE
────────────────────────────────────────
<<<{text}>>>
"""
def resolve_allowed_schema(mode: ExtractionMode):
    """
    Resolve allowed entity and relation types dynamically per call.
    """

    # Always allow BOOTSTRAP explicitly
    if mode == ExtractionMode.BOOTSTRAP:
        return None, None

    # IMPROVE mode → schema must exist AND be non-empty
    try:
        schema = extract_schema()
    except FileNotFoundError:
        # 🔴 No graph yet → must bootstrap
        return None, None

    entity_types = list(schema.get("entity_types", {}).keys())
    relation_types = list(schema.get("relation_types", {}).keys())

    # 🔴 CRITICAL FIX: empty schema ≠ IMPROVE
    if not entity_types and not relation_types:
        print(
            "⚠️ Empty graph schema detected. "
            "Falling back to BOOTSTRAP mode."
        )
        return SEED_ENTITY_TYPES, SEED_RELATION_TYPES

    return entity_types, relation_types

def load_suggested_rules():
    """
    Loads auto-generated extractor improvement rules.
    Used ONLY in IMPROVE mode.
    """
    if not os.path.exists(SUGGESTED_RULES_FILE):
        return []
    try:
        with open(SUGGESTED_RULES_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return []
# Canonical relation mapping
CANONICAL_RELATION_MAP = {
    "causes_failure": "failsDueTo",
    "reason_for_failure": "failsDueTo",
    "leading_to_failure": "failsDueTo",

    "mitigates": "maintainedBy",
    "prevents": "maintainedBy",
    "reduces": "maintainedBy",
}
def anchor_relations(relations, entities):
    """
    Attach source/target to inferred relations using nearby entities.
    """
    if not entities:
        return relations

    main_equipment = None
    for e in entities:
        if e["type"] in ["Equipment", "EquipmentType"]:
            main_equipment = e["id"]
            break

    anchored = []
    for r in relations:
        if r.get("source") is None or r.get("target") is None:
            if main_equipment:
                r["source"] = main_equipment
                r["target"] = r["target"] or main_equipment
        anchored.append(r)

    return anchored


def normalize_relation_type(rel_type: str) -> str:
    """
    Maps extracted or suggested relation names to canonical graph relations.
    """
    if not rel_type:
        return rel_type
    return CANONICAL_RELATION_MAP.get(rel_type.lower(), rel_type)
ENTITY_CANONICAL_MAP = {
    "sf6 cb": "SF6 Circuit Breaker",
    "sf6 circuit breaker": "SF6 Circuit Breaker",
    "245 kv breaker": "245 kV SF6 Circuit Breaker",

    "operating sequence": "Operating Sequence",
    "duty cycle": "Operating Sequence",

    "insulation failure": "Insulation Failure",
    "failure of insulation": "Insulation Failure",

    "sf6 leakage": "SF6 Leakage"
}


def normalize_entity_name(name: str) -> str:
    lname = name.lower().strip()
    return ENTITY_CANONICAL_MAP.get(lname, name)
def infer_entities_from_rules(entities, text):
    """
    Creates missing entities implied by suggested rules.
    """
    rules = load_suggested_rules()
    existing_names = {
        e["name"].lower()
        for e in entities
        if isinstance(e, dict) and "name" in e and isinstance(e["name"], str)
    }
    new_entities = []

    for rule in rules:
        rel = rule.get("mapped_relation", "").lower()

        # Failure-related entity inference
        if "failure" in rel and "failure" not in existing_names:
            new_entities.append({
                "id": "Failure_1",
                "type": "FailureMode",
                "name": "Insulation Failure"
            })

        # Mitigation-related entity inference
        if "mitigates" in rel and "maintenance" not in existing_names:
            new_entities.append({
                "id": "Maintenance_1",
                "type": "MaintenanceAction",
                "name": "Preventive Maintenance"
            })

    return entities + new_entities

def apply_suggested_rules(relations, text):
    """
    Adds relations inferred from suggested extractor rules.
    """
    rules = load_suggested_rules()
    new_relations = []

    for rule in rules:
        canonical = normalize_relation_type(rule.get("mapped_relation"))
        synonyms = rule.get("synonyms", [])

        for syn in synonyms:
            if syn.lower() in text.lower():
                new_relations.append({
                    "source": None,   # resolved later by entity linking
                    "target": None,
                    "type": canonical,
                    "evidence": f"Inferred via synonym: {syn}"
                })

    return relations + new_relations

def get_active_schema():
    if EXTRACTION_MODE == ExtractionMode.BOOTSTRAP:
        return {
            "entity_types": SEED_ENTITY_TYPES,
            "relation_types": SEED_RELATION_TYPES
        }
    else:
        from graph_schema import extract_schema
        return extract_schema()

import re

def extract_first_json_block(text: str) -> str:
    """
    Extracts the first valid JSON object from LLM output.
    Works even if text contains explanations or markdown.
    """
    # Try fenced JSON first
    fenced = re.search(r"```json\s*(\{.*?\})\s*```", text, re.DOTALL)
    if fenced:
        return fenced.group(1)

    # Fallback: first {...} block
    brace = re.search(r"(\{.*\})", text, re.DOTALL)
    if brace:
        return brace.group(1)

    raise ValueError("No JSON object found in LLM output")
def _clean_llm_json(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        text = text.split("```", 1)[1]
    if text.endswith("```"):
        text = text.rsplit("```", 1)[0]
    return text.strip()
# --------------------------------------------------
# 🔴 GLOBAL KEY SANITIZATION (LLM SAFETY NET)
# --------------------------------------------------

def _sanitize_keys(obj):
    """Remove trailing ':' from any dict keys recursively."""
    if isinstance(obj, dict):
        fixed = {}
        for k, v in obj.items():
            if isinstance(k, str) and k.endswith(":"):
                k = k[:-1]
            fixed[k] = _sanitize_keys(v)
        return fixed
    elif isinstance(obj, list):
        return [_sanitize_keys(x) for x in obj]
    else:
        return obj
def _validate_relations(relations):
    valid = []
    for r in relations:
        if not isinstance(r, dict):
            continue
        if not all(k in r for k in ("source", "target", "type")):
            continue
        if not isinstance(r["type"], str):
            continue
        valid.append(r)
    return valid



def extract_graph_elements(
    *,
    text: str,
    chapter: str,
    section: str,
    subsection: str,
    pages,
    chunk_id: int,
    mode: ExtractionMode = EXTRACTION_MODE,
    expected_relations: list[str] | None = None
):
    expected_relations = expected_relations or []

    expectation_block = ""
    if mode == ExtractionMode.IMPROVE and expected_relations:
        expectation_block = (
                "\n────────────────────────────────────────\n"
                "EXPECTED FACTS (MUST EXTRACT IF PRESENT)\n"
                "────────────────────────────────────────\n"
                "The following relations are KNOWN to be missing from the graph.\n"
                "If the text contains evidence for any of them, you MUST extract them:\n"
                f"- " + "\n- ".join(expected_relations) + "\n"
        )

    allowed_entity_types, allowed_relation_types = resolve_allowed_schema(mode)

    # 🔴 CRITICAL FIX: force BOOTSTRAP execution when seed schema is used
    if (
            mode == ExtractionMode.IMPROVE
            and allowed_entity_types == SEED_ENTITY_TYPES
            and allowed_relation_types == SEED_RELATION_TYPES
    ):
        mode = ExtractionMode.BOOTSTRAP

    if mode == ExtractionMode.BOOTSTRAP:
        print(
            f"🧪 Extractor[{chunk_id}] mode=BOOTSTRAP | "
            f"Schema discovery enabled (no filtering)"
        )
    else:
        print(
            f"🧪 Extractor[{chunk_id}] mode=IMPROVE | "
            f"{len(allowed_entity_types)} entity types | "
            f"{len(allowed_relation_types)} relation types"
        )

    prompt = EXTRACTION_PROMPT.format(
        mode=mode.value.upper(),
        chapter=chapter,
        section=section,
        subsection=subsection,
        pages=pages,
        allowed_entity_types= (", ".join(allowed_entity_types)
        if allowed_entity_types
        else "ALL ENTITY TYPES ALLOWED"),
        allowed_relation_types=(", ".join(allowed_relation_types)
        if allowed_relation_types
        else "ANY domain-relevant relations"),
        text=text
    )
    if mode == ExtractionMode.IMPROVE and not allowed_entity_types:
        raise RuntimeError(
            f"Extractor entered IMPROVE mode with empty schema "
            f"(chunk {chunk_id}). This is a fatal logic error."
        )

    response = call_llm(prompt)
    print(
        f"\n🧾 RAW LLM OUTPUT (chunk {chunk_id}, mode={mode}):\n"
        f"{response}\n"
    )
    try:
        json_text = extract_first_json_block(response)
        result = json.loads(json_text)
    except Exception as e:
        print(f"❌ JSON parse failed (chunk {chunk_id}): {e}")
        return {"entities": [], "relations": []}

    entities = result.get("entities", [])
    relations = result.get("relations", [])
    entities = _sanitize_keys(entities)
    relations = _sanitize_keys(relations)
    relations = _validate_relations(relations)
    KNOWN_RELATIONS = {
        "has_sequence", "has_attribute", "requires_maintenance",
        "monitored_by", "influences", "affects", "results_in"
    }

    for r in relations:
        tgt = r.get("target")
        r_type = r.get("type")

        if isinstance(tgt, str) and tgt in KNOWN_RELATIONS and r_type not in KNOWN_RELATIONS:
            r["type"], r["target"] = tgt, r_type

    # --------------------------------------------------
    # 🔴 Sanitize malformed relations (LLM safety)
    # --------------------------------------------------
    clean_relations = []

    for r in relations:
        if not isinstance(r, dict):
            continue

        if "type" not in r:
            print(
                f"⚠️ Dropping relation without 'type' "
                f"(chunk {chunk_id}): {r}"
            )
            continue

        if "source" not in r or "target" not in r:
            print(
                f"⚠️ Dropping relation without source/target "
                f"(chunk {chunk_id}): {r}"
            )
            continue

        clean_relations.append(r)

    relations = clean_relations

    print(
        f"🧠 PRE-MATERIALIZATION (chunk {chunk_id}): "
        f"{len(entities)} entities, {len(relations)} relations"
    )

    # 1️⃣ Normalize entity names (ALL MODES)
    for e in entities:
        if "name" in e:
            e["name"] = normalize_entity_name(e["name"])

    # 2️⃣ IMPROVE MODE: infer missing entities FIRST
    if mode == ExtractionMode.IMPROVE:
        entities = infer_entities_from_rules(entities, text)

    # 3️⃣ Normalize relation types (ALL MODES)
    for r in relations:
        if "type" in r:
            r["type"] = normalize_relation_type(r["type"])
    if mode == ExtractionMode.IMPROVE and expected_relations:
        extracted_types = {r["type"] for r in relations}
        missing = set(expected_relations) - extracted_types
        if missing:
            print(
                f"⚠️ Chunk {chunk_id}: expected relations not extracted → {missing}"
            )

    # 4️⃣ IMPROVE MODE: infer relations from rules
    if mode == ExtractionMode.IMPROVE:
        relations = apply_suggested_rules(relations, text)
    # FINAL STEP: anchor relations
    relations = anchor_relations(relations, entities)
    # 🔹 Domain-specific materialization (CRITICAL)
    entities, relations = materialize_domain_facts(
        entities,
        relations,
        text,
        chunk_id,
        mode=mode
    )
    entity_obs = observe_entities(entities)
    # --- PATCH: normalize relations with list-valued source/target ---

    normalized_relations = []

    for r in relations:
        src = r.get("source")
        tgt = r.get("target")
        r_type = r.get("type")
        evidence = r.get("evidence", "")

        # Expand list-valued targets
        if isinstance(tgt, list):
            for t in tgt:
                normalized_relations.append({
                    "source": src,
                    "target": t,
                    "type": r_type,
                    "evidence": evidence
                })

        # Expand list-valued sources (defensive, rare but possible)
        elif isinstance(src, list):
            for s in src:
                normalized_relations.append({
                    "source": s,
                    "target": tgt,
                    "type": r_type,
                    "evidence": evidence
                })

        else:
            normalized_relations.append(r)

    # Replace relations with normalized version
    relations = normalized_relations

    rel_obs = observe_relations(relations)
    save_observations(entity_obs, rel_obs)

    return {
        "entities": entities,
        "relations": relations
    }
