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
from core.rng import uniform, choice, randint
from collections import defaultdict
MAX_SMALL_BUILDINGS = 2
COLONIZATION_COST = {
            "compounds": 30,
            "biomass": 20,
            "fluidics": 15,
        }

class Planet:
    def __init__(self, radius=7):
        self.colonized = False
        self.owner = None 
        self.radius = radius
        self.hex_cap=4
        self.base_temperature = 0.0
        self.population = Population()
        max_active_hexes = int(self.population.size * 10)
        self.population_hub = PopulationHub()
        self.spaceport = None

        self.building_limits = defaultdict(int)
        self.buildings = []


        self.temperature = uniform(-1.5, 1.5)
        self.height = uniform(-1.5, 1.5)
        self.life = uniform(-1.5, 1.5)
        
        self.colonization_state = "none"
        # none | preparing | colonizing | colonized

        self.colonization_progress = 0.0
        self.colonization_time = 10.0  # ticków
        


        
        self.storage = {r: 80.0 for r in ALL_RESOURCES}

        self.hex_map = HexMap(radius)

        self.hex_map.apply_temperature_gradient(self.base_temperature)

        self.sources = []

        self._generate_sources()
        self._apply_sources()
        self._calculate_resources()
        self._determine_primary_resource()
        self.init_population_stats()



    def _generate_sources(self):
        sample_hexes = self.hex_map.hexes[:]



        for _ in range(3):
            h = choice(sample_hexes)
            self.sources.append(
                TemperatureSource(h.q, h.r, uniform(2, 3.0))
            )

        for _ in range(3):
            h = choice(sample_hexes)
            self.sources.append(
                HeightSource(h.q, h.r, uniform(2, 3))
            )

        for _ in range(3):
            h = choice(sample_hexes)
            self.sources.append(
                LifeSource(h.q, h.r, uniform(2, 3))
            )

        for _ in range(3):
            h = choice(sample_hexes)
            self.sources.append(
                ColdSource(h.q, h.r, uniform(2, 3))
            )

        for _ in range(3):
            h = choice(sample_hexes)
            self.sources.append(
                ErosionSource(h.q, h.r, uniform(2, 3.0))
            )
        for _ in range(3):
            h = choice(sample_hexes)
            self.sources.append(
                ToxicSource(h.q, h.r, uniform(2, 3))
            )


    def _apply_sources(self):

        for h in self.hex_map.hexes:
            h.temperature = 0.0
            h.height = 0.0
            h.life = 0.0

        for src in self.sources:
            for h in self.hex_map.hexes:
                value = src.influence(h)
                h.apply_parameter(src.param, value)

        for h in self.hex_map.hexes:
            h.temperature += self.temperature
            h.height += self.height
            h.life += self.life


    def _calculate_resources(self):
        for h in self.hex_map.hexes:
            calculate_resources(h)
            
    def sources_at(self, q, r):
        return [s for s in self.sources if s.q == q and s.r == r]
    
    def _determine_primary_resource(self):
        total = {}

        for h in self.hex_map.hexes:
            for res, val in h.resources.items():
                total[res] = total.get(res, 0) + val

        self.primary_resource = max(total, key=total.get)



    def produce(self):
        total = {}

        for h in self.hex_map.hexes:
            for b in h.buildings_small:
                out = b.produce(h, self.population)
                for r, v in out.items():
                    total[r] = total.get(r, 0) + v

        return total





    def tick(self):
        if self.colonization_state == "colonizing":
            self.colonization_progress += 1

            if self.colonization_progress >= self.colonization_time:
                self.finish_colonization()
        production = self.produce()

        for res, amount in production.items():
            if res not in self.storage:
                self.storage[res] = 0.0
            self.storage[res] += amount
        self.population.size *= 1.0 + (self.population.growth * self.population.happiness)
        
        for h in self.hex_map.hexes:
            for b in h.buildings_small:
                self.population.size -= b.pop_upkeep
                
        if self.colonized and not self.owner:
            print(" BUG: colonized planet without owner", id(self))


    def occupy_all_hexes(self):
        for h in self.hex_map.hexes:
            h.occupied = True


    def recalc_buildings(self):
        self.population_growth = 0.01
        self.hex_cap = 10

        for b in self.buildings:
            b.apply_planet_effect(self)


    def can_build(self, building):
        if not self.colonized:
            return building.name == "Space Port"
        key = building.limit_key()
        if key is None:
            return True
        return self.building_limits[key] == 0



    def build(self, hex, building):
        if not self.can_build(hex, building):
            return False

        if building.category == BUILDING_SMALL:
            hex.buildings_small.append(building)

        else:
            hex.building_major = building

        self.buildings.append(building)
        self.recalc_buildings()
        return True

    def add_building(self, building, hex):
        if not self.can_build(building):
            return False

        if building.blocks_hex():
            hex.blocked = True

        self.buildings.append(building)

        key = building.limit_key()
        if key:
            self.building_limits[key] += 1

        building.apply_planet_effect(self)
        return True


    def colonize(self, empire, galaxy):
        if self.colonized:
            return False

        self.colonized = True
        self.owner = empire
        self.colonized_turn = galaxy.turn

        if self not in empire.planets:
            empire.planets.append(self)

        return True

        
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

        # zapłać
        for res, cost in COLONIZATION_COST.items():
            empire.storage[res] -= cost

        self.owner = empire
        self.colonization_state = "colonizing"
        self.colonization_progress = 0.0
        self.is_new = True

        return True

    def finish_colonization(self):
        self.colonization_state = "colonized"
        self.colonized = True

        # startowa populacja
        self.population.size = 1.0

        # blokada: tylko Population Hub na start
        self.unlock_basic_buildings()

        print(f"[COLONY] Planet {id(self)} colonized by {self.owner.name}")


    def place_planet_unique(self, building):
        if self.has_building(building.name):
            return False
        self.planet_buildings.append(building)
        building.apply_planet_effect(self)
        return True
    
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
            if h.building_major:
                summary.append(f"{h.building_major.name} @ ({h.q},{h.r})")
            for b in h.buildings_small:
                summary.append(f"{b.name} @ ({h.q},{h.r})")
        return summary
    
    def build_spaceport(self, empire):
        if self.spaceport:
            return

        sp = SpacePort()
        sp.owner = empire       
        self.spaceport = sp
        self.colonized = True
        self.owner = empire

    def get_system(self, galaxy):
        for s in galaxy.systems:
            if self in s["system"].planets:
                return s["system"]
        return None

    def total_buildings(self):
        total = 0
        for h in self.hex_map.hexes:
            total += len(h.buildings_small)
            if h.building_major:
                total += 1
        return total

    def init_population_stats(self):
        stats = {
            "thermal": 0.0,
            "cryo": 0.0,
            "fluidics": 0.0,
            "solids": 0.0,
            "biomass": 0.0,
            "exotics": 0.0,
        }

        for h in self.hex_map.hexes:
            for res, val in h.resources.items():
                if val > stats[res]:
                    stats[res] = val

        self.population.stats = stats
