from buildings.Building import Building
from buildings.constants import BUILDING_PLANET_UNIQUE
from empire.Population import Population


from buildings.Building import Building
from buildings.constants import BUILDING_PLANET_UNIQUE
from empire.Population import Population


class SpacePort(Building):
    def __init__(self):
        super().__init__(
            name="Space Port",
            category=BUILDING_PLANET_UNIQUE,
            cost={"energy": 10, "minerals": 5},  # was: thermal, solids
            pop_cost=0.0,
            pop_required=0.0,
            pop_upkeep=-0.1
        )

    def build(self, planet, hex, source_planet=None):
        """
        🚀 KOLONIZACJA PLANETY
        - planet: planeta docelowa (nieskolonizowana)
        - hex: hex gdzie stawiamy SpacePort
        - source_planet: planeta źródłowa (ma zasoby i populację)
        """
        
        # 1️⃣ Sprawdzenie czy można zbudować
        if planet.colonized:
            return False, "Planet already colonized"
        
        if hex.is_blocked():
            return False, "Hex is blocked"
        
        if not hex.can_build(self, planet):
            return False, "Cannot build on this hex"
        
        # 2️⃣ Sprawdzenie source_planet
        if not source_planet:
            return False, "No source planet provided"
        
        if not source_planet.colonized:
            return False, "Source planet not colonized"
        
        # 3️⃣ Sprawdzenie zasobów na source_planet
        for res, amount in self.cost.items():
            if source_planet.storage.get(res, 0) < amount:
                return False, f"Source planet lacks {res}"
        
        # 4️⃣ Sprawdzenie populacji na source_planet
        if source_planet.population.size < 1.0:
            return False, "Source planet has insufficient population"
        
        # 5️⃣ Przypisanie właściciela (z source_planet)
        if not self.owner:
            self.owner = source_planet.owner
        
        # 6️⃣ Płatność z source_planet
        for res, amount in self.cost.items():
            source_planet.storage[res] -= amount
        
        # Zabierz populację ze źródła (kolonizatorzy)
        source_planet.population.size -= 1.0
        
        # 7️⃣ Umieszczenie budynku
        hex.add_building(self)
        
        # 8️⃣ Inicjalizacja kolonii
        planet.colonized = True
        planet.owner = self.owner
        planet.population = Population(size=5.0)
        planet.spaceport = self
        
        # 9️⃣ Dodanie do imperium
        if planet not in self.owner.planets:
            self.owner.planets.append(planet)
        
        # 🔟 Początkowe zasoby (z source_planet)
        planet.storage = {
            "energy": 10.0,
            "water": 10.0,
            "minerals": 10.0,
            "organics": 10.0,
            "gases": 10.0,
            "rare_elements": 10.0,
        }
        
        return True, f"Colony established on planet by {self.owner.name}"
    
    def apply_planet_effect(self, planet):
        """Wywoływane przez Building.build() - tutaj nie używane"""
        pass