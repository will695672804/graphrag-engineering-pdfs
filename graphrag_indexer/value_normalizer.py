# value_normalizer.py
import re
from typing import Optional, Dict

# -----------------------------
# UNIT NORMALIZATION TABLE
# -----------------------------

UNIT_MAP = {
    # Voltage
    "kv": ("voltage", 1e3, "V"),
    "v": ("voltage", 1.0, "V"),
    "kvp": ("voltage_peak", 1e3, "V"),

    # Current
    "ka": ("current", 1e3, "A"),
    "a": ("current", 1.0, "A"),

    # Power
    "mva": ("power", 1e6, "VA"),
    "kva": ("power", 1e3, "VA"),
    "mw": ("power", 1e6, "W"),
    "kw": ("power", 1e3, "W"),
    "mvar": ("reactive_power", 1e6, "VAr"),

    # Frequency
    "hz": ("frequency", 1.0, "Hz"),

    # Time
    "ms": ("time", 1e-3, "s"),
    "s": ("time", 1.0, "s"),
    "sec": ("time", 1.0, "s"),
    "min": ("time", 60.0, "s"),

    # Temperature
    "°c": ("temperature", 1.0, "C"),
    "c": ("temperature", 1.0, "C"),

    # Length / Distance
    "mm": ("length", 1e-3, "m"),
    "cm": ("length", 1e-2, "m"),
    "m": ("length", 1.0, "m"),
    "mm/kv": ("specific_creepage", 1e-3, "m/kV"),

    # Pressure
    "bar": ("pressure", 1e5, "Pa"),
    "mpa": ("pressure", 1e6, "Pa"),
    "kpa": ("pressure", 1e3, "Pa"),

    # Density
    "kg/m3": ("density", 1.0, "kg/m3"),

    # Resistance
    "ohm": ("resistance", 1.0, "ohm"),
    "ω": ("resistance", 1.0, "ohm"),

    # Percentage
    "%": ("ratio", 0.01, "pu"),

    # Moisture / Chemistry
    "ppm": ("concentration", 1.0, "ppm"),
    "mg/koh/g": ("acidity", 1.0, "mgKOH/g"),
}

# -----------------------------
# VALUE REGEX
# -----------------------------

VALUE_RE = re.compile(
    r"""
    (?P<value>\d+(\.\d+)?)
    \s*
    (?P<unit>
        kvp|kv|ka|mva|kva|mw|kw|mvar|
        hz|ms|sec|min|s|
        °c|c|
        mm/kv|mm|cm|m|
        bar|mpa|kpa|
        kg/m3|
        ohm|ω|
        %|ppm|mg/koh/g
    )
    """,
    re.IGNORECASE | re.VERBOSE
)

# -----------------------------
# MAIN NORMALIZER
# -----------------------------

def normalize_value(text: str) -> Optional[Dict]:
    """
    Extracts and normalizes the FIRST numeric value found in text.
    Returns SI-normalized value with metadata.
    """

    match = VALUE_RE.search(text.lower())
    if not match:
        return None

    raw_value = float(match.group("value"))
    raw_unit = match.group("unit").lower()

    if raw_unit not in UNIT_MAP:
        return None

    dimension, factor, si_unit = UNIT_MAP[raw_unit]

    return {
        "raw_text": match.group(0),
        "value": raw_value * factor,
        "si_unit": si_unit,
        "dimension": dimension,
        "original_value": raw_value,
        "original_unit": raw_unit
    }
