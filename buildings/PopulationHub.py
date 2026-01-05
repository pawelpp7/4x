from buildings.Building import Building
from buildings.constants import BUILDING_SMALL



class PopulationHub(Building):
    def __init__(self):
        super().__init__("Population Hub", BUILDING_SMALL, cost={"biomass": 10, "solids": 5},pop_upkeep=0.0,pop_cost=0.0)

    def apply_planet_effect(self, planet):
        planet.population.growth  += 0.02
        planet.hex_cap += 0.1
        
        
