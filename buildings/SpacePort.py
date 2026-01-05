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
