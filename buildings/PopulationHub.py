from buildings.Building import Building
from buildings.constants import BUILDING_SMALL
from core.config import BASIC_RESOURCES


class PopulationHub(Building):
    def __init__(self):
        super().__init__(
            "Population Hub", 
            category=BUILDING_SMALL, 
            cost={"organics": 10, "minerals": 5},  
            pop_upkeep=-0.8,
            pop_cost=0.0,
            cash=-0.2
        )

    def apply_planet_effect(self, planet):
        if not hasattr(planet, 'max_population'):
            planet.max_population = 100.0
        # Default boost
        planet.max_population += 50.0
        planet.hex_cap += 0.1

        # If this hub is placed on a hex whose local stats are near 0 (comfortable),
        # give an immediate population bonus and a larger capacity increase.
        try:
            built_hex = None
            for h in planet.hex_map.hexes:
                if self in h.buildings_small:
                    built_hex = h
                    break

            if built_hex:
                avg_abs = (abs(built_hex.temperature) + abs(built_hex.height) + abs(built_hex.life)) / 3.0
                # Comfortable hex: stats near 0 -> avg_abs small
                if avg_abs < 0.2:
                    # stronger bonus on good tiles
                    planet.max_population += 25.0
                    if hasattr(planet, 'population') and planet.population:
                        planet.population.size += 2.0
                elif avg_abs < 0.5:
                    planet.max_population += 10.0
                    if hasattr(planet, 'population') and planet.population:
                        planet.population.size += 1.0
        except Exception:
            pass

        
