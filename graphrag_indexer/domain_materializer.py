# domain_materializer.py

import re
import uuid
import json
from config import INDEX_DIR
from extraction_mode import ExtractionMode
with open(f"{INDEX_DIR}/canonical_entities.json") as f:
    ENTITY_CANONICAL_MAP = json.load(f)

with open(f"{INDEX_DIR}/canonical_relations.json") as f:
    CANONICAL_RELATION_MAP = json.load(f)
# ---------------- CANONICALIZATION HELPERS ---------------- #
ALLOWED_RELATIONS = set(CANONICAL_RELATION_MAP.values())
ALLOWED_ENTITY_TYPES = set(ENTITY_CANONICAL_MAP.values())
def canonicalize_entity(name: str) -> str:
    """
    Map surface entity names to canonical entity names.
    Falls back to original name if not found.
    """
    if not name:
        return name
    return ENTITY_CANONICAL_MAP.get(name.lower(), name)


def canonicalize_relation(rel: str) -> str:
    """
    Map surface relation phrases to canonical ontology relations.
    Falls back to original relation if not found.
    """
    if not rel:
        return rel
    return CANONICAL_RELATION_MAP.get(rel.lower(), rel)


def _new_entity(entity_type, name, chunk_id):
    return {
        "id": f"{entity_type}_{uuid.uuid4().hex[:8]}",
        "type": entity_type,
        "name": name,
        "chunk_id": chunk_id
    }


def _new_relation(src, tgt, rel_type, evidence, chunk_id):
    return {
        "source": src,
        "target": tgt,
        "type": rel_type,
        "evidence": evidence,
        "chunk_id": chunk_id
    }


def materialize_domain_facts(entities, relations, text, chunk_id,mode=None):
    """
    Materialize domain facts WITHOUT dropping extracted entities.
    """

    # 🔴 CRITICAL SAFETY: never drop entities in BOOTSTRAP
    if mode == ExtractionMode.BOOTSTRAP:
        return entities, relations
    new_entities = []
    new_relations = []

    entity_names = {e["name"].lower(): e["id"] for e in entities}

    # --------------------------------------------------
    # 1️⃣ Operating sequence (O-t-CO-T-CO)
    # --------------------------------------------------
    if re.search(r"\bO[-–]?t[-–]?CO[-–]?T[-–]?CO\b", text):
        raw_seq = "O-t-CO-T-CO"
        seq = canonicalize_entity(raw_seq)

        if "operating sequence" not in entity_names:
            seq_ent = _new_entity(
                "OperatingSequence",
                seq,
                chunk_id
            )
            new_entities.append(seq_ent)
            entity_names[seq.lower()] = seq_ent["id"]
        else:
            seq_ent = None

        for e in entities:
            if e["type"] in ("Equipment", "EquipmentType") and "sf6" in e["name"].lower():
                new_relations.append(
                    _new_relation(
                        e["id"],
                        entity_names[seq.lower()],
                        "hasOperatingSequence",
                        "Standard duty cycle for 245 kV SF6 circuit breakers",
                        chunk_id
                    )
                )

    # --------------------------------------------------
    # 2️⃣ Insulation failure causes
    # --------------------------------------------------
    if "insulation" in text.lower() and "failure" in text.lower():
        raw_failure = "insulation failure"
        failure = canonicalize_entity(raw_failure)

        if failure.lower() not in entity_names:
            fail_ent = _new_entity(
                "FailureMode",
                failure,
                chunk_id
            )
            new_entities.append(fail_ent)
            entity_names[failure.lower()] = fail_ent["id"]

        causes = [
            "abnormal ageing",
            "design defect",
            "manufacturing problem",
            "material defect",
            "poor maintenance",
            "lightning surge",
            "short circuit"
        ]

        for cause in causes:
            if cause in text.lower():
                cause_ent = _new_entity(
                    "FailureCause",
                    cause.title(),
                    chunk_id
                )
                new_entities.append(cause_ent)

                new_relations.append(
                    _new_relation(
                        entity_names[failure.lower()],
                        cause_ent["id"],
                        canonicalize_relation("causes failure"),
                        f"Identified in text as cause: {cause}",
                        chunk_id
                    )

                )

    # --------------------------------------------------
    # 3️⃣ SF6 leakage mitigation
    # --------------------------------------------------
    if "sf6" in text.lower() and "leak" in text.lower():
        raw_leak = "sf6 leakage"
        leak = canonicalize_entity(raw_leak)

        if leak.lower() not in entity_names:
            leak_ent = _new_entity(
                "FailureMode",
                leak,
                chunk_id
            )
            new_entities.append(leak_ent)
            entity_names[leak.lower()] = leak_ent["id"]

        actions = {
            "regular inspection": "Regular inspection",
            "leakage test": "Leakage test with halogen detector",
            "dew point": "Monitoring dew point",
            "pressure monitoring": "Pressure monitoring",
            "vacuum": "Evacuation before refilling"
        }

        for key, label in actions.items():
            if key in text.lower():

                # ---- Canonicalize entity ----
                canonical_label = canonicalize_entity(label)
                entity_type = "MaintenanceAction"

                # ---- Entity ontology guard ----
                if entity_type not in ALLOWED_ENTITY_TYPES:
                    continue

                # ---- Avoid duplicate canonical entities ----
                if canonical_label.lower() in entity_names:
                    act_ent_id = entity_names[canonical_label.lower()]
                else:
                    act_ent = _new_entity(
                        entity_type,
                        canonical_label,
                        chunk_id
                    )
                    new_entities.append(act_ent)
                    act_ent_id = act_ent["id"]
                    entity_names[canonical_label.lower()] = act_ent_id

                # ---- Canonicalize + guard relation ----
                rel_type = canonicalize_relation("mitigates")

                if rel_type not in ALLOWED_RELATIONS:
                    continue

                new_relations.append(
                    _new_relation(
                        entity_names[leak.lower()],
                        act_ent_id,
                        rel_type,
                        f"Maintenance action identified: {canonical_label}",
                        chunk_id
                    )
                )

    return (
        entities + new_entities,
        relations + new_relations
    )
