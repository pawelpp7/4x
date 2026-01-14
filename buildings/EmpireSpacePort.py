from buildings.Building import Building
from buildings.constants import BUILDING_EMPIRE_UNIQUE
from core.config import BASIC_RESOURCES
from empire.Population import Population
from planet.resources import ALL_RESOURCES

class EmpireSpacePort(Building):
    def __init__(self):
        super().__init__(
            name="Empire Space Port",
            category=BUILDING_EMPIRE_UNIQUE,
            cost={},  # darmowy / startowy
        )

    def produce(self, hex, population):
        return {res: 10.0 for res in BASIC_RESOURCES}

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
        planet.population = Population(size=10.0)
        planet.population.planet = planet
        try:
            planet.set_owner(self.owner)
        except Exception:
            # fallback: direct assign
            planet.owner = self.owner
            try:
                if self.owner and planet not in self.owner.planets:
                    self.owner.planets.append(planet)
            except Exception:
                pass

        planet.init_population_stats()
        planet.storage = {r: 0.0 for r in ALL_RESOURCES}
        planet.storage = {r: 10.0 for r in BASIC_RESOURCES}




        return True, "Empire SpacePort established (starting colony)"