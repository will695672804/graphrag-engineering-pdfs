import json
from pathlib import Path

REGISTRY_PATH = "index/type_registry.json"
OUT_PATH = "index/type_hierarchy.json"

# ----------------------------
# Load registry
# ----------------------------
with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
    registry = json.load(f)


# ----------------------------
# Subtype inference rule
# ----------------------------
def is_subtype(child: str, parent: str, registry: dict) -> bool:
    """
    Returns True if 'child' is a subtype of 'parent'
    based on structural similarity.
    """

    if child == parent:
        return False

    child_rels = set(registry[child]["common_out_relations"])
    parent_rels = set(registry[parent]["common_out_relations"])

    child_attrs = set(registry[child]["common_attributes"])
    parent_attrs = set(registry[parent]["common_attributes"])

    if not child_rels or not parent_rels:
        return False

    rel_overlap = len(child_rels & parent_rels) / len(child_rels)

    # conservative rules
    return (
        rel_overlap >= 0.8 and
        child_attrs.issubset(parent_attrs) and
        registry[child]["count"] < registry[parent]["count"]
    )


# ----------------------------
# Call is_subtype() HERE
# ----------------------------
hierarchy = []

types = list(registry.keys())

for child in types:
    for parent in types:
        if is_subtype(child, parent, registry):
            hierarchy.append({
                "child": child,
                "parent": parent
            })

# ----------------------------
# Persist hierarchy
# ----------------------------
Path(OUT_PATH).parent.mkdir(parents=True, exist_ok=True)

with open(OUT_PATH, "w", encoding="utf-8") as f:
    json.dump(hierarchy, f, indent=2)

print(f"[OK] Type hierarchy written to {OUT_PATH}")
