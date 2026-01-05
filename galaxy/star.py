# galaxy/star.py
from core.rng import choice

STAR_TYPES = {
    "red_dwarf": {
        "temp_bias": -0.5,
        "planet_count": (3, 6)
    },
    "yellow": {
        "temp_bias": 0.0,
        "planet_count": (4, 8)
    },
    "blue_giant": {
        "temp_bias": 0.7,
        "planet_count": (6, 10)
    }
}

class Star:
    def __init__(self):
        self.type = choice(list(STAR_TYPES.keys()))
        data = STAR_TYPES[self.type]

        self.temp_bias = data["temp_bias"]
        self.planet_range = data["planet_count"]
