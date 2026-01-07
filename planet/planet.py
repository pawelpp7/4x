# planet/planet.py

from buildings.PopulationHub import PopulationHub
from buildings.SpacePort import SpacePort
from planet.hex_map import HexMap
from empire.Population import Population
from planet.sources import (
    TemperatureSource,
    HeightSource,
    LifeSource,
    ColdSource,
    ErosionSource,
    ToxicSource,
)
from planet.resources import calculate_resources, ALL_RESOURCES
from buildings.constants import BUILDING_SMALL, BUILDING_PLANET_UNIQUE
from core.rng import uniform, choice
from collections import defaultdict

ENERGY_PER_FREE_POP = 0.3
MAX_SMALL_BUILDINGS = 2

MAX_STAT_RANGE = 8.0


COLONIZATION_COST = {
    "compounds": 30,
    "biomass": 20,
    "fluidics": 15,
}


class Planet:
    def __init__(self, radius=5):
        self.colonized = False
        self.owner = None
        self.radius = radius

        self.population = None
        self.population_hub = PopulationHub()
        self.spaceport = None

        self.building_limits = defaultdict(int)
        self.buildings = []

        # planetarne biasy
        self.temperature = uniform(-1.5, 1.5)
        self.height = uniform(-1.5, 1.5)
        self.life = uniform(-1.5, 1.5)

        self.colonization_state = "none"
        self.colonization_progress = 0.0
        self.colonization_time = 10.0

        self.storage = {r: 0.0 for r in ALL_RESOURCES}
        
        self.hex_cap=2

        self.hex_map = HexMap(radius)

        self.sources = []
        self._generate_sources()
        self._apply_sources()
        self._calculate_resources()
        self._determine_primary_resource()

    # ------------------------------------------------------------------
    # SOURCES / HEXES
    # ------------------------------------------------------------------

    def _generate_sources(self):
        sample_hexes = self.hex_map.hexes[:]

        for _ in range(3):
            h = choice(sample_hexes)
            self.sources.append(TemperatureSource(h.q, h.r, uniform(2, 3)))

        for _ in range(3):
            h = choice(sample_hexes)
            self.sources.append(HeightSource(h.q, h.r, uniform(2, 3)))

        for _ in range(3):
            h = choice(sample_hexes)
            self.sources.append(LifeSource(h.q, h.r, uniform(2, 3)))

        for _ in range(3):
            h = choice(sample_hexes)
            self.sources.append(ColdSource(h.q, h.r, uniform(2, 3)))

        for _ in range(3):
            h = choice(sample_hexes)
            self.sources.append(ErosionSource(h.q, h.r, uniform(2, 3)))

        for _ in range(3):
            h = choice(sample_hexes)
            self.sources.append(ToxicSource(h.q, h.r, uniform(2, 3)))

    def _apply_sources(self):
        for h in self.hex_map.hexes:
            h.temperature = 0.0
            h.height = 0.0
            h.life = 0.0

        for src in self.sources:
            for h in self.hex_map.hexes:
                h.apply_parameter(src.param, src.influence(h))

        # planetarne przesunięcie
        for h in self.hex_map.hexes:
            h.temperature += self.temperature
            h.height += self.height
            h.life += self.life
            
    def sources_at(self, q, r):
        return [s for s in self.sources if s.q == q and s.r == r]


    def _calculate_resources(self):
        for h in self.hex_map.hexes:
            calculate_resources(h)
            
    def get_location(self, galaxy):
        for entry in galaxy.systems:
            system = entry["system"]
            if self in system.planets:
                orbit = system.planets.index(self)
                return system, orbit
        return None, None
    
    def buildings_summary(self):
        summary = []
        for h in self.hex_map.hexes:
            if getattr(h, "building_major", None):
                summary.append(f"{h.building_major.name} @ ({h.q},{h.r})")
            for b in h.buildings_small:
                summary.append(f"{b.name} @ ({h.q},{h.r})")
        return summary
    
    def total_buildings(self):
        total = 0
        for h in self.hex_map.hexes:
            total += len(h.buildings_small)
            if getattr(h, "building_major", None):
                total += 1
        return total


    def extreme_level(self, stat_name):
        """
        0.0 – planeta jednorodna
        1.0 – ekstremalnie niestabilna
        """
        MAX_RANGE = 8.0
        return min(1.0, self.stat_range(stat_name) / MAX_RANGE)



    # ------------------------------------------------------------------
    # RESOURCES / POPULATION
    # ------------------------------------------------------------------

    def _determine_primary_resource(self):
        total = {}
        for h in self.hex_map.hexes:
            for res, val in h.resources.items():
                total[res] = total.get(res, 0) + val
        self.primary_resource = max(total, key=total.get)

    def init_population_stats(self):
        stats = {r: 0.0 for r in ALL_RESOURCES}
        for h in self.hex_map.hexes:
            for res, val in h.resources.items():
                if val > stats[res]:
                    stats[res] = val
        self.population.stats = stats
        
    def can_build(self, building):
        if not self.colonized:
            return building.name == "Space Port"
        key = building.limit_key()
        if key is None:
            return True
        return self.building_limits[key] == 0

    # ------------------------------------------------------------------
    # EXTREMES / INSTABILITY
    # ------------------------------------------------------------------

    def stat_range(self, stat_name):
        values = [getattr(h, stat_name) for h in self.hex_map.hexes]
        return max(values) - min(values)

    def instability(self):
        temp = min(1.0, self.stat_range("temperature") / MAX_STAT_RANGE)
        height = min(1.0, self.stat_range("height") / MAX_STAT_RANGE)
        life = min(1.0, self.stat_range("life") / MAX_STAT_RANGE)

        return (
            temp * 0.4 +
            height * 0.3 +
            life * 0.3
        )

    # ------------------------------------------------------------------
    # PRODUCTION
    # ------------------------------------------------------------------

    def produce(self):
        if not self.colonized or self.population is None:
            return {}

        total_output = {}
        total_energy_cost = 0.0

        # reset użycia populacji na tick
        self.population.used = 0.0

        for h in self.hex_map.hexes:
            for b in h.buildings_small:
                workers = getattr(b, "workers_required", 0.0)

                # brak ludzi → budynek nie działa
                if not self.population.can_support(workers):
                    continue

                # przydziel ludzi
                self.population.add_load(workers)

                # produkcja
                out = b.produce(h, self.population)
                for r, v in out.items():
                    total_output[r] = total_output.get(r, 0.0) + v

                # koszt energii zależny od ekstremów planety
                base_energy = getattr(b, "energy_cost", 0.0)
                total_energy_cost += base_energy * (1.0 + self.instability())

        # zapłać energię imperium
        if self.owner:
            self.owner.energy -= total_energy_cost


        return total_output


    # ------------------------------------------------------------------
    # TICK
    # ------------------------------------------------------------------

    def tick(self):
        if not self.colonized or self.population is None:
            return
        if self.colonization_state == "colonizing":
            self.colonization_progress += 1
            if self.colonization_progress >= self.colonization_time:
                self.finish_colonization()

        production = self.produce()

        for res, amount in production.items():
            self.storage[res] = self.storage.get(res, 0.0) + amount

        inst = self.instability()
        inst = self.instability()
        growth_mod = max(0.2, 1.0 - inst) 

        self.population.size *= 1.0 + self.population.growth * growth_mod


    # ------------------------------------------------------------------
    # ENERGY
    # ------------------------------------------------------------------

    def energy_delta(self):
        if not self.colonized or self.population is None:
            return {}

        return self.population.free * ENERGY_PER_FREE_POP

    # ------------------------------------------------------------------
    # COLONIZATION
    # ------------------------------------------------------------------

    def can_colonize(self, empire):
        if self.colonization_state != "none":
            return False
        if self.owner is not None:
            return False
        return empire.has_spaceport_in_system(self)

    def start_colonization(self, empire):
        if not self.can_colonize(empire):
            return False

        for res, cost in COLONIZATION_COST.items():
            if empire.storage.get(res, 0) < cost:
                return False

        for res, cost in COLONIZATION_COST.items():
            empire.storage[res] -= cost

        self.owner = empire
        self.colonization_state = "colonizing"
        self.colonization_progress = 0.0
        return True

    def finish_colonization(self):
        self.colonization_state = "colonized"
        self.colonized = True
        self.population = Population(size=1.0)
        self.init_population_stats()
        self.storage = {r: 10.0 for r in ALL_RESOURCES}
        print(f"COLONY Planet {id(self)} colonized by {self.owner.name}")
