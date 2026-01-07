from buildings.Building import Building
from buildings.constants import BUILDING_EMPIRE_UNIQUE
from core.config import BASIC_RESOURCES
from empire.Population import Population

class EmpireSpacePort(Building):
    def __init__(self):
        super().__init__(
            name="Empire Space Port",
            category=BUILDING_EMPIRE_UNIQUE,
            cost={},  # darmowy / startowy
        )

    def produce(self, hex, population):
        return {res: 1.0 for res in BASIC_RESOURCES}

    def build(self, planet, hex):
        if hex.is_blocked():
            return False, "Cannot build on blocked hex"

        if not hex.can_build(self):
            return False, "Cannot build Empire SpacePort here"

        # postaw budynek
        hex.building_major = self
        planet.spaceport = self

        # inicjalizacja kolonii
        planet.colonized = True
        planet.owner = self.owner
        planet.population = Population(size=5.0)

        self.owner.planets.append(planet)

        return True, "Empire SpacePort established (starting colony)"