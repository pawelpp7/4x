# planet/resources.py
from core.config import LOW_THRESHOLD, HIGH_THRESHOLD

RESOURCE_MAP = {
    "temperature": {
        "low": "cryo",
        "high": "thermal"
    },
    "height": {
        "low": "fluidics",
        "high": "solids"
    },
    "life": {
        "low": "exotics",
        "high": "biomass"
    }
}

ALL_RESOURCES = [
    "thermal",
    "cryo",
    "fluidics",
    "solids",
    "biomass",
    "exotics",
]

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
        res["thermal"] = t - t_th
    elif t < -t_th:
        res["cryo"] = abs(t) - t_th

    if h > h_th:
        res["solids"] = h - h_th
    elif h < -h_th:
        res["fluidics"] = abs(h) - h_th

    if l > l_th:
        res["biomass"] = l - l_th
    elif l < -l_th:
        res["exotics"] = abs(l) - l_th

    hex.resources = res
