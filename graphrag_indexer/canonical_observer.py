# canonical_observer.py

from collections import defaultdict
import json

ENTITY_SURFACE_FILE = "index/entity_surface_forms.json"
REL_SURFACE_FILE = "index/relation_surface_forms.json"


def observe_entities(entities):
    surface = defaultdict(set)
    for e in entities:
        surface[e["type"]].add(e["name"].lower())
    return surface


def observe_relations(relations):
    surface = defaultdict(set)
    for r in relations:
        rel_type = r.get("type")
        if not rel_type:
            continue

        surface.setdefault(rel_type, set()).add(rel_type)

    return surface


def save_observations(entity_obs, rel_obs):
    def _merge(path, obs):
        try:
            with open(path) as f:
                existing = json.load(f)
        except:
            existing = {}

        for k, vals in obs.items():
            existing.setdefault(k, [])
            for v in vals:
                if v not in existing[k]:
                    existing[k].append(v)

        with open(path, "w") as f:
            json.dump(existing, f, indent=2)

    _merge(ENTITY_SURFACE_FILE, entity_obs)
    _merge(REL_SURFACE_FILE, rel_obs)
