from buildings.Building import Building
from buildings.constants import BUILDING_PLANET_UNIQUE


class SpacePort(Building):
    def __init__(self, empire):
        super().__init__("Space Port", BUILDING_PLANET_UNIQUE,cost={"thermal": 10, "solids": 5},owner=empire)
        
    def __init__(self):
        super().__init__(
            name="Space Port",
            category=BUILDING_PLANET_UNIQUE
        )

    def apply_planet_effect(self, planet):
        planet.colonized = True
        planet.owner = self.owner
        

