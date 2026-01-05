import random
from buildings.registry import BUILDINGS
from buildings.PopulationHub import PopulationHub
from buildings.SpacePort import SpacePort
from buildings.Mining import MiningComplex

class SimpleAI:
    def __init__(self, empire, galaxy):
        self.empire = empire
        self.cooldown = 0
        self.galaxy = galaxy

    def tick(self):
        self.cooldown -= 10
        if self.cooldown > 0:
            return
        self.cooldown = 1

        planet = self.pick_planet()
        if not planet:
            return

        # 🔹 KOLONIZACJA - buduj SpacePort
        if not planet.colonized:
            print(f"AI]Colonizing planet {id(planet)}")
            
            spaceport = SpacePort()
            spaceport.owner = self.empire
            
            free_hex = next((h for h in planet.hex_map.hexes if not h.is_blocked()), None)
            if not free_hex:
                print("AI No free hex for SpacePort")
                return
            
            # 🔨 NOWA LOGIKA - używamy build()
            success, msg = spaceport.build(planet, free_hex)
            if success:
                print(f"AI {msg} - Planet colonized by {self.empire.name}")
            else:
                print(f"AI Failed to build SpacePort: {msg}")
            return

        # 🔹 ROZWÓJ - buduj inne budynki
        hex = self.pick_hex(planet)
        if not hex:
            print("AI No valid hex")
            return

        building = self.pick_building(planet, hex)
        if not building:
            print("AI No building choice")
            return

        # Ustaw właściciela
        building.owner = self.empire

        # 🔨 NOWA LOGIKA - używamy build()
        success, msg = building.build(planet, hex)
        if success:
            print(f"AI {msg} on hex ({hex.q},{hex.r}) resources={hex.resources}")
        else:
            print(f"AI Build failed: {msg}")

    def pick_planet(self):
        if self.empire.planets:
            return random.choice(self.empire.planets)

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

        max_val = max(sum(h.resources.values()) for h in free_hexes) if free_hexes else 0
        if max_val == 0:
            return random.choice(free_hexes)
            
        top_hexes = [h for h in free_hexes if sum(h.resources.values()) >= 0.8 * max_val]
        return random.choice(top_hexes) if top_hexes else random.choice(free_hexes)

    def pick_building(self, planet, hex):
        P = planet.population.size
        B = planet.total_buildings()

        # Population Hub - gdy jest już kilka budynków
        if B > 0 and P > (B / 5):
            return PopulationHub()

        # Kopalnie według zasobów hexa
        if hex.resources:
            best_res = max(hex.resources, key=hex.resources.get)
            # Mapowanie resource -> building name
            mine_mapping = {
                "thermal": "Thermal Mine",
                "cryo": "Cryo Mine",
                "solids": "Solids Mine",
                "fluidics": "Fluidics Mine",
                "biomass": "Biomass Mine",
                "compounds": "Compounds Mine",
            }
            mine_name = mine_mapping.get(best_res)
            if mine_name:
                factory = BUILDINGS.get(mine_name)
                if factory:
                    return factory()

        return None