from buildings.Building import Building
from buildings.constants import BUILDING_SMALL
from empire.buffs import population_resource_bonus

class MiningComplex(Building):
    def __init__(self, resource, efficiency=1.0):
        super().__init__(
            name=f"{resource} extractor",
            category=BUILDING_SMALL,
            cost={
                "solids": 5,
                "exotics": 3,
            },
            pop_upkeep=0.1,
            energy = -0.3
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
        
