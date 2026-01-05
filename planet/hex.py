# planet/hex.py
from buildings.constants import BUILDING_MAJOR
MAX_SMALL_BUILDINGS = 2

class Hex:
    def __init__(self, q, r):
        self.q = q
        self.r = r
        self.MAX_SMALL_BUILDINGS = 2
        self.temperature = 0.0
        self.height = 0.0
        self.life = 0.0

        self.resources = {}

        # 🔹 budynki
        self.building_major = None          # jeden duży / planet_unique
        self.buildings_small = []            # lista małych

        self.occupied = False                # np. UI / debug

    def is_blocked(self):
        return self.building_major is not None

    def apply_parameter(self, param, value):
        if param == "temperature":
            self.temperature += value
        elif param == "height":
            self.height += value
        elif param == "life":
            self.life += value

    def produce_hex(self, planet_population):
        prod = {}

        # ❌ duży budynek blokuje naturalne zasoby
        if self.building_major and self.building_major.blocks_hex():
            return prod

        # ✅ naturalne zasoby
        for res, val in self.resources.items():
            prod[res] = val

        # ✅ małe budynki
        for b in self.buildings_small:
            add = b.produce(self, planet_population)
            for r, v in add.items():
                prod[r] = prod.get(r, 0) + v

        return prod
    def can_build(self, building, planet=None):


        if planet and not planet.can_build(building):
            return False
        
        if planet and not planet.colonized:
            return building.name == "Space Port"

        if building.category == BUILDING_MAJOR:
            return self.building_major is None

        return len(self.buildings_small) < self.MAX_SMALL_BUILDINGS

    def add_building(self, building):
        if building.category == BUILDING_MAJOR:
            self.building_major = building
        else:
            self.buildings_small.append(building)

                
    def production_summary(self, population):
        summary = {}
        for b in self.buildings_small:
            out = b.produce(self, population)
            for r, v in out.items():
                summary[r] = summary.get(r, 0) + v
        return summary

    def population_load(self):
        load = 0.0
        for b in self.buildings_small:
            load += b.pop_upkeep
        return load

    def population_hex_color(hex, planet):
        load = hex.population_load()

        if load <= 0:
            return (60, 120, 60)

        ratio = min(1.0, load / max(0.1, planet.population.size))

        if ratio < 0.3:
            return (80, 160, 80)
        elif ratio < 0.6:
            return (200, 180, 80)
        else:
            return (200, 80, 80)
