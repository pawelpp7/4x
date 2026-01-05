from buildings.constants import BUILDING_EMPIRE_UNIQUE, BUILDING_MAJOR,BUILDING_SYSTEM_UNIQUE,BUILDING_PLANET_UNIQUE, BUILDING_SMALL
from buildings.Building import Building
from empire.buffs import population_resource_bonus

class ResourceBuilding(Building):
    def __init__(self, resource, efficiency=1.0):
        super().__init__(
            name=f"{resource} extractor",
            category=BUILDING_SMALL,
            cost={
                "solids": 5,
                "exotics": 3,
            },
            pop_upkeep=0.1
        )
        self.resource = resource
        self.efficiency = efficiency


    def produce(self, hex, population):
        if self.resource not in hex.resources:
            return {}

        base = hex.resources[self.resource]
        pop_bonus = population_resource_bonus(population, self.resource)

        return {
            self.resource: base * self.efficiency * pop_bonus
        }
        
