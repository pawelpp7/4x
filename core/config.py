# core/config.py

SEED = 41

# progi parametrów
LOW_THRESHOLD = -0.3
HIGH_THRESHOLD = 0.3

# siła wpływu źródeł
SOURCE_FALLOFF = 0.3

# rozmiary
PLANET_RADIUS_MIN = 6
PLANET_RADIUS_MAX = 12


BUILDING_SMALL = "small"
BUILDING_MAJOR = "major"
BUILDING_PLANET_UNIQUE = "planet_unique"


BASIC_RESOURCES = [
    "thermal",
    "cryo",
    "solids",
    "fluidics",
    "biomass",
    "exotics",
]

ADVANCED_RESOURCES = [
    "compounds",
    "alloys",
    "polymers",
    "biochips",
    "coolants",
    "nanomaterials",
]


ENVIRONMENT_WEIGHTS = {
    "compounds": {
        "temperature": 0.2,
        "toxic": 0.3
    },
    "alloys": {
        "height": 0.3,
        "temperature": 0.1
    },
    "polymers": {
        "life": 0.3,
        "temperature": -0.2
    },
    "biochips": {
        "life": 0.5
    },
    "coolants": {
        "cold": 0.4
    },
    "nanomaterials": {
        "height": 0.4,
        "toxic": 0.2
    }
}
