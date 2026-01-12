from buildings.Building import Building
from buildings.constants import BUILDING_PLANET_UNIQUE
from core.config import BASIC_RESOURCES
from empire.Population import Population


from buildings.Building import Building
from buildings.constants import BUILDING_PLANET_UNIQUE
from empire.Population import Population


class SpacePort(Building):
    def __init__(self):
        super().__init__(
            name="Space Port",
            category=BUILDING_PLANET_UNIQUE,
            cost={"energy": 10, "minerals": 5},
            pop_cost=0.0,
            pop_required=0.0,
            pop_upkeep=-0.1
        )

    def build(self, target_planet, hex, source_planet=None):
        """POPRAWIONA WERSJA - bez desync"""
        
        # --- KOLONIZACJA ---
        if source_planet is not None:
            
            # 1️⃣ Sprawdź zasoby SOURCE
            for res, cost in self.cost.items():
                if source_planet.storage.get(res, 0) < cost:
                    return False, "Source planet lacks resources"
            
            # 2️⃣ Odejmij zasoby z SOURCE
            for res, cost in self.cost.items():
                source_planet.storage[res] -= cost
            
            # 3️⃣ Ustaw właściciela PRZED rozpoczęciem kolonizacji
            # ✅ POPRAWKA: Użyj set_owner() lub ręcznie dodaj do listy
            if hasattr(target_planet, 'set_owner'):
                target_planet.set_owner(self.owner)
            else:
                # Bezpieczna zmiana właściciela
                old_owner = target_planet.owner
                if old_owner and old_owner != self.owner:
                    if target_planet in old_owner.planets:
                        old_owner.planets.remove(target_planet)
                
                target_planet.owner = self.owner
                
                if self.owner and target_planet not in self.owner.planets:
                    self.owner.planets.append(target_planet)
            
            # 4️⃣ Rozpocznij kolonizację
            target_planet.colonization_state = "colonizing"
            target_planet.colonization_progress = 0.0
            
            # 5️⃣ Postaw budynek
            hex.add_building(self)
            
            return True, f"Colonization started from source planet"
        
        # --- NORMALNA BUDOWA (jeśli kiedyś będzie potrzebna) ---
        return False, "SpacePort requires source planet for colonization"

    def produce(self, hex, population):
            return {res: 1.0 for res in BASIC_RESOURCES}
        
    def apply_planet_effect(self, planet):
            """Wywoływane przez Building.build() - tutaj nie używane"""
            pass