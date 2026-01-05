import random
from buildings.registry import BUILDINGS
from buildings.PopulationHub import PopulationHub
from buildings.SpacePort import SpacePort
from buildings.Mining import MiningComplex
from buildings.Refinery import Refinery

class SimpleAI:
    def __init__(self, empire,galaxy):
        self.empire = empire
        self.cooldown = 0
        self.galaxy=galaxy

    def tick(self):
        # odliczamy cooldown
        self.cooldown -= 1
        if self.cooldown > 0:
            return
        self.cooldown = 1  # AI działa co tick

        # wybór planety
        planet = self.pick_planet()
        if not planet:
            return

        # kolonizacja planety
        if not planet.colonized:
            print(f"[AI] Colonizing planet {id(planet)}")
            planet.colonize(self.empire, self.galaxy)
            planet.build_spaceport(self.empire)

            return

        # wybór hexu
        hex = self.pick_hex(planet)
        if not hex:
            print("[AI] No valid hex")
            return

        # wybór budynku
        building = self.pick_building(planet, hex)
        if not building:
            print("[AI] No building choice")
            return

        # sprawdzenie czy można budować
        if not hex.can_build(building):
            print("[AI] Hex full")
            return

        if not building.can_afford(planet):
            print("[AI] Cannot afford", building.name)
            return

        # płatność i budowa
        building.pay_cost(planet)
        building.owner = self.empire 
        hex.add_building(building)
        building.apply_planet_effect(planet)

        print(f"[AI] Built {building.name} on hex ({hex.q},{hex.r}) resources={hex.resources}")
        system = planet.get_system(self.galaxy)
        print(f"[AI] {self.empire.name} building in system {id(system)} planet {id(planet)}")


    def pick_planet(self):
        # 1️⃣ jeśli mamy planety – rozwijaj je
        if self.empire.planets:
            return random.choice(self.empire.planets)

        # 2️⃣ jeśli nie – znajdź pierwszą wolną planetę w galaktyce
        for entry in self.galaxy.systems:
            for p in entry["system"].planets:
                if not p.colonized:
                    return p
        return None



    def pick_hex(self, planet):
        free_hexes = [
            h for h in planet.hex_map.hexes
            if not h.is_blocked() or len(h.buildings_small) < h.MAX_SMALL_BUILDINGS
        ]
        if not free_hexes:
            return None

        # losowo spośród top 80% zasobów
        max_val = max(sum(h.resources.values()) for h in free_hexes)
        top_hexes = [h for h in free_hexes if sum(h.resources.values()) >= 0.8 * max_val]
        return random.choice(top_hexes)




    def pick_building(self, planet, hex):
        P = planet.population.size
        B = planet.total_buildings()

        # 🔹 Population Hub – tylko gdy ma sens
        if B > 0 and P > (B / 5):
            return PopulationHub()

        # 🔹 kopalnie według zasobów
        if hex.resources:
            best_res = max(hex.resources, key=hex.resources.get)
            return BUILDINGS.get(best_res)

        return None

