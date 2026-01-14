# planet/planet.py

from buildings.PopulationHub import PopulationHub
from buildings.SpacePort import SpacePort
from core.config import BASIC_RESOURCES
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
from planet.resources import ALL_RESOURCES, calculate_resources
from military.units import PlanetMilitaryManager
from buildings.constants import BUILDING_SMALL, BUILDING_PLANET_UNIQUE
from core.rng import uniform, choice
from collections import defaultdict
import logging

ENERGY_PER_FREE_POP = 0.3
MAX_SMALL_BUILDINGS = 2

MAX_STAT_RANGE = 8.0


COLONIZATION_COST = {
    "rare_elements": 30,
    "organics": 20,
    "water": 15,
}


class Planet:
    def __init__(self, radius=5):
        self.colonized = False
        self.owner = None
        self.radius = radius

        self.population = Population(size=0.0)
        self.population_hub = PopulationHub()
        self.spaceport = None
        self.shield_strength=100.0
        self.shield_max=100.0
        self.orbital_platforms=[]
        
        self.military_units = []
        self.military_level = 0
        
        self.max_population = 100.0  # bazowy cap

        self.building_limits = defaultdict(int)
        self.buildings = []
        self.morale_regen = 0.05

        # planetarne biasy
        self.temperature = uniform(-1.5, 1.5)
        self.height = uniform(-1.5, 1.5)
        self.life = uniform(-1.5, 1.5)

        self.colonization_state = "none"
        self.colonization_progress = 0.0
        self.colonization_time = 10.0

        self.storage = {}

        for res in ALL_RESOURCES:
            self.storage[res] = 0.0
        self.hex_cap = 2

        self.hex_map = HexMap(radius)

        self.sources = []
        self._generate_sources()
        self._apply_sources()
        self._calculate_resources()
        self._determine_primary_resource()
        self.military_manager = PlanetMilitaryManager(self)
        self.production_speed = 1.0

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
        stats = {r: 0.0 for r in BASIC_RESOURCES}
        for h in self.hex_map.hexes:
            for res, val in h.resources.items():
                if val > stats[res]:
                    stats[res] = val
        self.population.stats = stats
        
    def can_build(self, building):
        if building.name == "Space Port" :
            if  self.colonization_state == "none":
                return True
            else:
                return False

        if not self.colonized:
            return False

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
        if not self.colonized or self.population.size == 0:
            return {}

        total = {}
        self.population.used = 0.0

        for h in self.hex_map.hexes:

            # SMALL
            for b in h.buildings_small:
                self._process_building(b, h, total)

            # MAJOR
            if h.building_major:
                self._process_building(h.building_major, h, total)

        return total


    # ------------------------------------------------------------------
    # TICK
    # ------------------------------------------------------------------


    def tick(self):
        if self.colonization_state == "colonizing":
            self.colonization_progress += 1
            if self.colonization_progress >= self.colonization_time:
                self.finish_colonization()

        if not self.colonized:
            return

        # Jeśli planeta skolonizowana, ale populacja wygasła -> dekolonizuj
        if self.population.size <= 0.0:
            try:
                import logging
                logging.info("kolonia wymarła %s", id(self))
            except Exception:
                pass
            self.set_owner(None)
            return
        production = self.produce()

        for res, amount in production.items():
            self.storage[res] = self.storage.get(res, 0.0) + amount
        
        if self.colonized and self.population.size > 0:
            self.military_manager.tick()

        # ✅ NOWE - Shield regeneration
        if self.shield_strength>0 and self.shield_strength < self.shield_max:
            self.shield_strength = min(
                self.shield_max,
                self.shield_strength + self.shield_regen
            )
        
        # ✅ NOWE - Orbital platforms regeneration
        for platform in self.orbital_platforms:
            if platform["health"] < platform["max_health"]:
                platform["health"] = min(
                    platform["max_health"],
                    platform["health"] + platform["regen"]
                )

        # ⚖️ ZBALANSOWANY WZROST POPULACJI
        
        # 1️⃣ Bazowy wzrost (z planet.population.growth, domyślnie 0.01 = 1%)
        inst = self.instability()
        growth_mod = max(0.2, 1.0 - inst)

        # ✅ Harmony bonus: if local hex parameters (temp/height/life) are close to 0
        # then population grows faster. Compute average absolute deviation per-hex
        # and give a modest bonus when avg_abs < 0.5 (up to +50% growth_mod).
        try:
            avg_abs = 0.0
            for h in self.hex_map.hexes:
                avg_abs += (abs(h.temperature) + abs(h.height) + abs(h.life)) / 3.0
            avg_abs /= max(1, len(self.hex_map.hexes))
            # Stronger harmony bonus: if hex stats are near 0 (avg_abs -> 0)
            # grant up to +100% growth_mod. Scale linearly so avg_abs==0 -> +1.0, avg_abs>=0.6 -> +0
            max_threshold = 0.6
            raw = max(0.0, max_threshold - avg_abs)
            harmony_norm = raw / max_threshold
            harmony_bonus = harmony_norm  # up to 1.0
            growth_mod *= (1.0 + harmony_bonus)
        except Exception:
            logging.debug("Failed computing harmony bonus for planet %s", id(self))
        
        # 2️⃣ Carrying capacity (max populacja)
        max_pop = getattr(self, 'max_population', 100.0)  # domyślnie 100
        current_pop = self.population.size
        
        # 3️⃣ Logistic growth - spowalnia gdy zbliżamy się do cap
        # Formula: growth * (1 - current/max)
        capacity_factor = max(0.0, 1.0 - (current_pop / max_pop))
        
        # 4️⃣ Oblicz faktyczny wzrost
        # Procentowy wzrost, ale ograniczony przez capacity
        growth_rate = self.population.growth * growth_mod * capacity_factor
        absolute_growth = current_pop * growth_rate
        
        # 5️⃣ Zastosuj wzrost
        self.population.size += absolute_growth
        
        # 6️⃣ Hard cap (nigdy powyżej max)
        self.population.size = min(self.population.size, max_pop)
        
        if self.population.size<=0.0:
            import logging
            logging.info("kolonia wymarła %s", id(self))
            self.set_owner(None)


    # ------------------------------------------------------------------
    # ENERGY
    # ------------------------------------------------------------------

    def cash_delta(self):
        if not self.colonized or self.population.size==0:
            return 0

        return self.population.free * ENERGY_PER_FREE_POP


    def sell_excess(self, empire, resource, keep_amount, price_per_unit):
        """Sell planet's excess `resource` above `keep_amount` to `empire` at `price_per_unit`.

        Returns revenue (0.0 if nothing sold).
        """
        try:
            available = self.storage.get(resource, 0.0)
            amount = max(0.0, available - keep_amount)
            if amount <= 0.0:
                return 0.0
            # Do NOT mutate planet storage here: `empire.sell_resources`
            # is responsible for validating and deducting the sold amount.
            revenue = empire.sell_resources(self, resource, amount, price_per_unit)
            logging.info("Planet %s sold %.1f %s for %.2f", id(self), amount, resource, revenue)
            return revenue
        except Exception:
            return 0.0

    # ------------------------------------------------------------------
    # COLONIZATION
    # ------------------------------------------------------------------

    def can_colonize(self, empire):
        if self.colonization_state != "none":
            return False
        if self.owner is not None:
            return False
        return True



    def finish_colonization(self):
        """POPRAWIONA WERSJA"""
        self.colonization_state = "colonized"
        self.colonized = True
        
        # ✅ POPRAWKA: Sprawdź czy już jest w liście
        if self.owner and self not in self.owner.planets:
            self.owner.planets.append(self)
            try:
                import logging
                logging.info("COLONY Planet %s colonized by %s", id(self), self.owner.name)
            except Exception:
                pass
        elif self.owner and self in self.owner.planets:
            try:
                import logging
                logging.info("COLONY Planet %s already in %s list", id(self), self.owner.name)
            except Exception:
                pass
        
        # Inicjalizacja
        if not self.population or self.population.size == 0:
            self.population = Population(size=1.0)
        
        self.init_population_stats()
        
        # Storage jeśli nie ma
        from core.config import BASIC_RESOURCES
        if not hasattr(self, 'storage') or not self.storage:
            self.storage = {r: 10.0 for r in BASIC_RESOURCES}


    def _process_building(self, b, hex, total):
        workers = getattr(b, "workers_required", 0.0)
        
        if not self.population.can_support(workers):
            return

        delta = b.produce(hex, self.population)

        # 1️⃣ SPRAWDŹ INPUTY
        for res, val in delta.items():
            if val < 0 and self.storage.get(res, 0.0) < -val:
                return  # brak surowców → budynek nie działa

        # 2️⃣ ZASTOSUJ DELTĘ
        for res, val in delta.items():
            self.storage[res] = self.storage.get(res, 0.0) + val
            total[res] = total.get(res, 0.0) + val

        self.population.add_load(workers)



    def get_center_hex(self):
        return min(
            self.hex_map.hexes,
            key=lambda h: abs(h.q) + abs(h.r)
        )

    def has_spaceport(self):
        for h in self.hex_map.hexes:
            if h.building_major and h.building_major.name == "Space Port":
                return True
        return False

    def set_owner(self, new_empire):
        """
        Bezpiecznie zmienia właściciela planety
        Usuwa z listy starego, dodaje do nowego
        """
        # Usuń ze starego właściciela jeśli jest inny
        if self.owner and self.owner != new_empire:
            if self in self.owner.planets:
                self.owner.planets.remove(self)
                try:
                    print(f"[OWNERSHIP] Removed planet from {self.owner.name}")
                except Exception:
                    pass

        # Jeśli new_empire to None (lub sentinel), wyczyść właściciela
        if new_empire is None or new_empire == "none":
            self.owner = None
            return

        # Dodaj do nowego właściciela jeśli to obiekt Empire
        self.owner = new_empire
        try:
            if self not in new_empire.planets:
                new_empire.planets.append(self)
                print(f"[OWNERSHIP] Added planet to {new_empire.name}")
        except Exception:
            # Nie zakładaj, że new_empire ma listę `planets`
            pass