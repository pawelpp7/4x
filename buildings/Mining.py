from buildings.Building import Building
from buildings.constants import BUILDING_SMALL
from empire.buffs import population_resource_bonus

class MiningComplex(Building):
    def __init__(self, resource, efficiency=1.0):
        super().__init__(
            name=f"{resource.capitalize()} Extractor",
            category=BUILDING_SMALL,
            cost={
                "minerals": 5,  # was: solids
                "rare_elements": 3,  # was: exotics
            },
            pop_upkeep=0.1,
            cash=-0.3
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


# Export
__all__ = ['MiningComplex']