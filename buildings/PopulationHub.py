from buildings.Building import Building
from buildings.constants import BUILDING_SMALL


class PopulationHub(Building):
    def __init__(self):
        super().__init__(
            "Population Hub", 
            category=BUILDING_SMALL, 
            cost={"organics": 10, "minerals": 5},  # was: biomass, solids
            pop_upkeep=0.5,
            pop_cost=0.0,
            energy=-0.2
        )

    def apply_planet_effect(self, planet):
        """
        🏘️ POPULATION HUB EFFECT
        - Zwiększa maksymalną populację planety (carrying capacity)
        - Zwiększa hex_cap (więcej budynków na hex)
        """
        if not hasattr(planet, 'max_population'):
            planet.max_population = 100.0
        
        planet.max_population += 50.0
        planet.hex_cap += 0.1