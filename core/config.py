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


# ============================================
# TIER 1: BASIC RESOURCES (Mining/Extraction)
# ============================================
BASIC_RESOURCES = [
    "energy",         # was: thermal - heat, power
    "water",          # was: fluidics - H2O, liquids
    "minerals",       # was: solids - metals, ores, rocks
    "organics",       # was: biomass - biological matter
    "gases",          # was: cryo - atmospheric gases
    "rare_elements",  # was: exotics - rare materials, anomalies
]

# ============================================
# TIER 2: REFINED RESOURCES (Refineries)
# ============================================
ADVANCED_RESOURCES = [
    "alloys",         # minerals + energy → construction
    "chemicals",      # gases + water + energy → industry
    "biotech",        # organics + water → medicine, food
    "plastics",       # organics + chemicals → components
    "electronics",    # minerals + rare_elements → computers
    "fuel",           # organics + chemicals + gases → power
]

# ============================================
# TIER 3: STRATEGIC RESOURCES (6 Pillars)
# ============================================
# These connect to planet sources:
# Temperature → Authority (control, order)
# Height → Faith (mountains = temples, connection to divine)
# Life → Culture (diversity breeds art)
# Cold → Science (calm, calculated research)
# Erosion → Arcane (chaos, reality tears)
# Toxic → Military (harsh conditions breed warriors)

STRATEGIC_RESOURCES = [
    "authority",  # TemperatureSource - control, government
    "faith",      # HeightSource - religion, spirituality
    "culture",    # LifeSource - art, influence
    "science",    # ColdSource - research, technology
    "arcane",     # ErosionSource - magic, chaos
    "military",   # ToxicSource - warfare, defense
]


# Mapowanie źródeł planet → strategiczne zasoby
SOURCE_TO_STRATEGIC = {
    "temperature": "authority",
    "height": "faith",
    "life": "culture",
    "cold": "science",
    "erosion": "arcane",
    "toxic": "military",
}


ENVIRONMENT_WEIGHTS = {
    "alloys": {
        "temperature": 0.3,  # heat for smelting
        "height": 0.1        # pressure
    },
    "chemicals": {
        "temperature": 0.2,
        "toxic": 0.3
    },
    "biotech": {
        "life": 0.5,
        "temperature": -0.2  # stable temps better
    },
    "plastics": {
        "life": 0.3,
        "temperature": 0.2
    },
    "electronics": {
        "height": 0.2,       # rare minerals in mountains
        "toxic": -0.3        # clean environment needed
    },
    "fuel": {
        "life": 0.4,         # organic matter
        "height": 0.2        # pressure
    }
}