# canonicalizer.py
from canonical_entities import *

ALL_MAPS = [
    (EQUIPMENT, "Equipment"),
    (EQUIPMENT_TYPES, "EquipmentType"),
    (COMPONENTS, "Component"),
    (MATERIALS, "Material"),
    (PARAMETERS, "Parameter"),
    (MAINTENANCE_ACTIONS, "MaintenanceAction"),
    (FAILURE_MODES, "FailureMode"),
    (PROTECTION_SCHEMES, "ProtectionScheme"),
    (STANDARDS, "Standard")
]

def canonicalize(name: str):
    n = name.lower().strip()

    for mapping, etype in ALL_MAPS:
        for canon, variants in mapping.items():
            if n == canon or n in variants:
                return canon, etype

    return n, "Unknown"
