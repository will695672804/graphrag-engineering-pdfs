"""
Semantic canonicalizer for entities and relations.
- Embedding-based clustering
- Context-aware canonical naming
- Ontology-drift safe
"""

import json
import os
from collections import defaultdict
from typing import List

import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.cluster import AgglomerativeClustering

from config import INDEX_DIR

# ---------------- SAFETY CONFIG ---------------- #

ALLOWED_ENTITY_TYPES = {
    "Equipment",
    "EquipmentType",
    "Component",
    "FailureMode",
    "FailureCause",
    "MaintenanceAction",
    "OperatingSequence",
    "Parameter",
    "Rating",
    "Standard"
}

ALLOWED_RELATIONS = {
    "failsDueTo",
    "mitigatedBy",
    "maintainedBy",
    "hasOperatingSequence",
    "hasParameter",
    "hasRating",
    "compliesWith"
}

# Thresholds
ENTITY_SIM_THRESHOLD = 0.78
RELATION_SIM_THRESHOLD = 0.75

# Files
SURFACE_ENTITIES_FILE = f"{INDEX_DIR}/entity_surface_forms.json"
SURFACE_RELATIONS_FILE = f"{INDEX_DIR}/relation_surface_forms.json"

CANONICAL_ENTITIES_FILE = f"{INDEX_DIR}/canonical_entities.json"
CANONICAL_RELATIONS_FILE = f"{INDEX_DIR}/canonical_relations.json"

# ---------------- HELPERS ---------------- #

def cosine_sim(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


def load_json(path, default):
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return default


# ---------------- CORE LOGIC ---------------- #

class SemanticCanonicalizer:

    def __init__(self):
        self.embedder = SentenceTransformer("all-MiniLM-L6-v2")

    def _cluster(self, embeddings, threshold):
        if len(embeddings) < 2:
            return [[0]]

        clustering = AgglomerativeClustering(
            n_clusters=None,
            metric="cosine",
            linkage="average",
            distance_threshold=1 - threshold
        )
        labels = clustering.fit_predict(embeddings)

        clusters = defaultdict(list)
        for idx, label in enumerate(labels):
            clusters[label].append(idx)
        return list(clusters.values())

    # -------- ENTITIES -------- #

    def canonicalize_entities(self, surface_entities):
        canonical_map = {}

        for entity_type, examples in surface_entities.items():
            if entity_type not in ALLOWED_ENTITY_TYPES:
                print(f"⚠️ Skipping unknown entity type: {entity_type}")
                continue

            texts = [
                f"{e['surface']} :: {e['context']}"
                for e in examples
            ]
            embeddings = self.embedder.encode(texts)

            clusters = self._cluster(embeddings, ENTITY_SIM_THRESHOLD)

            for cluster in clusters:
                members = [examples[i]["surface"] for i in cluster]

                canonical = self._choose_canonical_name(
                    members,
                    entity_type
                )

                for m in members:
                    canonical_map[m.lower()] = canonical

        return canonical_map

    # -------- RELATIONS -------- #

    def canonicalize_relations(self, surface_relations):
        canonical_map = {}

        for examples in surface_relations:
            texts = [
                f"{r['surface']} :: {r['context']}"
                for r in examples
            ]
            embeddings = self.embedder.encode(texts)

            clusters = self._cluster(embeddings, RELATION_SIM_THRESHOLD)

            for cluster in clusters:
                members = [examples[i]["surface"] for i in cluster]

                canonical = self._choose_relation_name(members)

                if canonical not in ALLOWED_RELATIONS:
                    print(f"⚠️ Rejected relation '{canonical}' (ontology guard)")
                    continue

                for m in members:
                    canonical_map[m.lower()] = canonical

        return canonical_map

    # -------- SAFETY-CONTROLLED NAMING -------- #

    def _choose_canonical_name(self, members: List[str], entity_type: str):
        """
        Deterministic, ontology-safe naming.
        No free-form LLM invention allowed.
        """
        # Prefer longest, most technical-looking term
        members = sorted(members, key=len, reverse=True)
        candidate = members[0].title()

        return candidate

    def _choose_relation_name(self, members: List[str]):
        """
        Hard mapping only. No invention allowed.
        """
        joined = " ".join(members).lower()

        if any(k in joined for k in ["cause", "lead", "result"]):
            return "failsDueTo"
        if any(k in joined for k in ["mitigate", "reduce", "prevent"]):
            return "mitigatedBy"
        if any(k in joined for k in ["maintain", "inspection", "test"]):
            return "maintainedBy"

        return None


# ---------------- MAIN ---------------- #

def main():
    surface_entities = load_json(SURFACE_ENTITIES_FILE, {})
    surface_relations = load_json(SURFACE_RELATIONS_FILE, [])

    canonicalizer = SemanticCanonicalizer()

    print("🧠 Canonicalizing entities...")
    entity_map = canonicalizer.canonicalize_entities(surface_entities)

    print("🧠 Canonicalizing relations...")
    relation_map = canonicalizer.canonicalize_relations(surface_relations)

    with open(CANONICAL_ENTITIES_FILE, "w") as f:
        json.dump(entity_map, f, indent=2)

    with open(CANONICAL_RELATIONS_FILE, "w") as f:
        json.dump(relation_map, f, indent=2)

    print("✅ Canonical maps written")
    print(f"  → {CANONICAL_ENTITIES_FILE}")
    print(f"  → {CANONICAL_RELATIONS_FILE}")


if __name__ == "__main__":
    main()
