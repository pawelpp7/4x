from buildings.Building import Building
from core.config import BUILDING_MAJOR


class Refinery(Building):
    def __init__(self, resource_in, resource_out):
        name = f"{resource_in.capitalize()} Refinery"
        super().__init__(name, BUILDING_MAJOR, cost={resource_in: 5})
        self.resource_in = resource_in
        self.resource_out = resource_out

    def produce(self, hex, population):
        prod = {}
        if self.resource_in in hex.resources:

            prod[self.resource_out] = hex.resources[self.resource_in] * 0.5
        return prod

    def apply_planet_effect(self, planet):
        pass
