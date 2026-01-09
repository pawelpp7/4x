from buildings.Building import Building
from buildings.constants import BUILDING_PLANET_UNIQUE
from empire.Population import Population


from buildings.Building import Building
from buildings.constants import BUILDING_PLANET_UNIQUE
from empire.Population import Population


class SpacePort(Building):
    def __init__(self):
        super().__init__(
            name="Space Port",
            category=BUILDING_PLANET_UNIQUE,
            cost={"energy": 10, "minerals": 5},  # was: thermal, solids
            pop_cost=0.0,
            pop_required=0.0,
            pop_upkeep=-0.1
        )

    def build(self, target_planet, hex, source_planet=None):

        # --- KOLONIZACJA ---
        if source_planet is not None:

            # 1️⃣ Sprawdź zasoby SOURCE
            for res, cost in self.cost.items():
                if source_planet.storage.get(res, 0) < cost:
                    return False, "Source planet lacks resources"

            # 2️⃣ Odejmij zasoby z SOURCE
            for res, cost in self.cost.items():
                source_planet.storage[res] -= cost

            # 3️⃣ Rozpocznij kolonizację
            target_planet.owner = self.owner
            target_planet.colonization_state = "colonizing"
            target_planet.colonization_progress = 0.0

            hex.add_building(self)
        

            return True, f"Colonization started from source planet"

        
        def apply_planet_effect(self, planet):
            """Wywoływane przez Building.build() - tutaj nie używane"""
            pass