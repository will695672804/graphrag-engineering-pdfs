import json
from pathlib import Path

ONTOLOGY_IN = "index/ontology.json"
ONTOLOGY_OUT = "index/ontology_seeded.json"

# -----------------------------
# Minimal, defensible hierarchy
# -----------------------------
SEED_SUBCLASSES = [
    ("Component", "Equipment"),
    ("Connection", "Component"),

    ("FailureMode", "Failure"),
    ("FailureCause", "Failure"),
    ("Cause", "FailureCause"),

    ("MeasurementInstrument", "Measurement"),
    ("Parameter", "Measurement"),
    ("Feature", "Measurement"),

    ("MaintenanceAction", "Process"),
    ("Program", "Process"),

    ("Software", "Program"),
    ("Mode", "Process"),
]

with open(ONTOLOGY_IN, "r", encoding="utf-8") as f:
    ontology = json.load(f)

existing = {
    (s["child"], s["parent"])
    for s in ontology.get("subclasses", [])
}

seeded = []

for child, parent in SEED_SUBCLASSES:
    if child in ontology["classes"] and parent in ontology["classes"]:
        if (child, parent) not in existing:
            seeded.append({
                "child": child,
                "parent": parent,
                "source": "seeded"
            })

ontology.setdefault("subclasses", [])
ontology["subclasses"].extend(seeded)

Path(ONTOLOGY_OUT).parent.mkdir(exist_ok=True)

with open(ONTOLOGY_OUT, "w", encoding="utf-8") as f:
    json.dump(ontology, f, indent=2)

print(f"[OK] Seeded {len(seeded)} subclass relations")
