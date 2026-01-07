from buildings.Building import Building
from buildings.constants import BUILDING_PLANET_UNIQUE


class SpacePort(Building):
    def __init__(self):
        super().__init__(
            name="Space Port",
            category=BUILDING_PLANET_UNIQUE,
            cost={"thermal": 10, "solids": 5},
            pop_cost=0.0,
            pop_required=0.0,
            pop_upkeep=-0.1
        )
        


    def apply_planet_effect(self, planet):
        planet.colonized = True
        planet.owner = self.owner

        if planet not in self.owner.planets:
            self.owner.planets.append(planet)

        planet.spaceport = self
        
    

    def can_build(self, planet, empire):
        # nie można budować na skolonizowanej planecie
        if planet.colonized:
            return False, "Planet already colonized"

        # znajdź planety imperium z wystarczającymi zasobami
        valid_sources = []
        for p in empire.planets:
            if all(p.storage.get(r, 0) >= c for r, c in self.cost.items()):
                valid_sources.append(p)

        if not valid_sources:
            return False, "No source planet with required resources"

        return True, valid_sources
    
    def build(self, target_planet, empire, source_planet):
    # zapłać koszty z planety źródłowej
        for r, c in self.cost.items():
            source_planet.storage[r] -= c

        target_planet.spaceport = self
        target_planet.owner = empire
        target_planet.colonization_state = "colonizing"
        target_planet.colonization_progress = 0.0

        return True, "Colonization started"
