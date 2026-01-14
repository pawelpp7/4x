# planet/resources.py
from core.config import LOW_THRESHOLD, HIGH_THRESHOLD

RESOURCE_MAP = {
    "temperature": {
        "low": "gases",
        "high": "energy"
    },
    "height": {
        "low": "water",
        "high": "minerals"
    },
    "life": {
        "low": "rare_elements",
        "high": "organics"
    }
}

ALL_RESOURCES = [
    "energy",         # was: thermal - heat, power
    "water",          # was: fluidics - H2O, liquids
    "minerals",       # was: solids - metals, ores, rocks
    "organics",       # was: biomass - biological matter
    "gases",          # was: cryo - atmospheric gases
    "rare_elements",  # was: exotics - rare materials, anomalies
    "alloys",         # minerals + energy → construction
    "chemicals",      # gases + water + energy → industry
    "biotech",        # organics + water → medicine, food
    "plastics",       # organics + chemicals → components
    "electronics",    # minerals + rare_elements → computers
    "fuel",           # organics + chemicals + gases → power
    
]

RESOURCE_EXTREMES = {
    "energy":  "temperature",
    "gases":     "temperature",
    "water": "erosion",
    "minerals":   "height",
    "organics":  "life",
    "rare_elements":  "toxic",
}

RESOURCE_THRESHOLDS = {
    "temperature": 0.10,
    "height": 0.15,
    "life": 0.18
}


def calculate_resources(hex):
    res = {}

    t = hex.temperature
    h = hex.height
    l = hex.life

    t_th = RESOURCE_THRESHOLDS["temperature"]
    h_th = RESOURCE_THRESHOLDS["height"]
    l_th = RESOURCE_THRESHOLDS["life"]

    if t > t_th:
        res["energy"] = t - t_th
    elif t < -t_th:
        res["gases"] = abs(t) - t_th

    if h > h_th:
        res["minerals"] = h - h_th
    elif h < -h_th:
        res["water"] = abs(h) - h_th

    if l > l_th:
        res["organics"] = l - l_th
    elif l < -l_th:
        res["rare_elements"] = abs(l) - l_th

    hex.resources = res


