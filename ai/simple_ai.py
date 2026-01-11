import random
from buildings.registry import BUILDINGS
from buildings.PopulationHub import PopulationHub
from buildings.SpacePort import SpacePort
from buildings.Mining import MiningComplex

class SimpleAI:
    def __init__(self, empire, galaxy):
        self.empire = empire
        self.galaxy = galaxy
        self.cooldown = 0
        self.colonization_cooldown = 0

    def tick(self):
        """Główna pętla AI - z transportem"""
        self.cooldown -= 1
        self.colonization_cooldown -= 1
        
        if self.cooldown > 0:
            return
        
        self.cooldown = 5

        # 1️⃣ PRIORYTET: KOLONIZACJA
        if self.colonization_cooldown <= 0 and len(self.empire.planets) < 15:
            if self.try_colonize():
                self.colonization_cooldown = 10
                return

        # ✅ 2️⃣ Transport zasobów (co 3 tury)
        if self.galaxy.turn % 3 == 0:
            if self.try_transport_resources():
                return

        # 3️⃣ Rozwój istniejących planet
        if self.empire.planets:
            planet = self.pick_development_planet()
            if planet:
                self.develop_planet(planet)

    def try_colonize(self):
        """Próbuje skolonizować nową planetę"""
        
        if not self.empire.planets:
            return False
        
        # 1️⃣ Znajdź valid source planets
        valid_sources = []
        for p in self.empire.planets:
            if not p.colonized or not p.population:
                continue
            
            # Sprawdź zasoby dla SpacePort (energy=10, minerals=5)
            if (p.storage.get('energy', 0) >= 12 and 
                p.storage.get('minerals', 0) >= 7 and
                p.population.size >= 1.5):
                valid_sources.append(p)
        
        if not valid_sources:
            return False
        
        # Wybierz source z największymi zasobami
        source = max(valid_sources, 
                    key=lambda p: p.storage.get('energy', 0) + p.storage.get('minerals', 0))
        
        # 2️⃣ Znajdź target
        target = self.find_colonization_target(source)
        if not target:
            return False
        
        # 3️⃣ Znajdź wolny hex na target
        free_hex = next(
            (h for h in target.hex_map.hexes if not h.is_blocked()),
            None
        )
        if not free_hex:
            return False
        
        # 4️⃣ Zbuduj SpacePort
        spaceport = SpacePort()
        spaceport.owner = self.empire
        
        success, msg = spaceport.build(target, free_hex, source)
        
        if success:
            print(f"[AI {self.empire.name}] {msg}")
            return True
        else:
            print(f"[AI {self.empire.name}] Colonization failed: {msg}")
        
        return False

    def find_colonization_target(self, source_planet):
        """Znajduje najlepszą planetę do kolonizacji"""
        
        # Znajdź system source_planet
        source_system = None
        for entry in self.galaxy.systems:
            if source_planet in entry["system"].planets:
                source_system = entry
                break
        
        if not source_system:
            return None
        
        candidates = []
        
        # 1️⃣ Planety w tym samym systemie
        for p in source_system["system"].planets:
            if not p.colonized and p != source_planet:
                score = self.evaluate_planet_resources(p) * 2  # bonus
                candidates.append((p, score))
        
        # 2️⃣ Planety w sąsiednich systemach
        for neighbor in source_system["links"]:
            for p in neighbor["system"].planets:
                if not p.colonized:
                    score = self.evaluate_planet_resources(p)
                    candidates.append((p, score))
        
        if not candidates:
            return None
        
        # Sortuj po score i wybierz z top 30%
        candidates.sort(key=lambda x: -x[1])
        top_count = max(1, len(candidates) // 3)
        
        return random.choice(candidates[:top_count])[0]

    def evaluate_planet_resources(self, planet):
        """Ocenia wartość planety"""
        total = 0.0
        for h in planet.hex_map.hexes:
            total += sum(h.resources.values())
        return total

    def pick_development_planet(self):
        """Wybiera planetę do rozwoju"""
        if not self.empire.planets:
            return None
        
        candidates = []
        
        for p in self.empire.planets:
            if not p.colonized or not p.population:
                continue
            
            free_hexes = [
                h for h in p.hex_map.hexes
                if not h.is_blocked() and h.can_build(PopulationHub(), p)
            ]
            
            if free_hexes:
                # Priorytet: zasoby > populacja
                score = (
                    sum(p.storage.values()) / 50 +
                    len(free_hexes) * 2 +
                    p.population.size
                )
                candidates.append((p, score))
        
        if not candidates:
            return None
        
        candidates.sort(key=lambda x: -x[1])
        return candidates[0][0]

    def develop_planet(self, planet):
        """Rozwija wybraną planetę"""
        
        hex = self.pick_hex(planet)
        if not hex:
            return
        
        building = self.pick_building(planet, hex)
        if not building:
            return
        
        building.owner = self.empire
        success, msg = building.build(planet, hex)
        
        if success:
            print(f"[AI {self.empire.name}] {msg}")

    def pick_hex(self, planet):
        """Wybiera najlepszy hex do budowy"""
        free_hexes = [
            h for h in planet.hex_map.hexes
            if (not h.is_blocked() or 
                len(h.buildings_small) < planet.hex_cap)
        ]
        
        if not free_hexes:
            return None
        
        hex_scores = []
        for h in free_hexes:
            score = sum(h.resources.values())
            if not h.buildings_small:
                score += 0.5
            hex_scores.append((h, score))
        
        hex_scores.sort(key=lambda x: -x[1])
        top_count = max(1, len(hex_scores) // 5)
        top_hexes = [h for h, _ in hex_scores[:top_count]]
        
        return random.choice(top_hexes)

    def pick_building(self, planet, hex):
        """Wybiera najlepszy budynek"""
        
        P = planet.population.size
        B = planet.total_buildings()
        
        # 1️⃣ Population Hub - tylko gdy bardzo mało pop
        if B > 5 and P < (B * 0.15):
            hub = PopulationHub()
            if hex.can_build(hub, planet) and hub.can_afford(planet):
                return hub
        
        # 2️⃣ Kopalnie - główny priorytet
        if hex.resources:
            best_res = max(hex.resources, key=hex.resources.get)
            best_val = hex.resources[best_res]
            
            if best_val > 0.15:  # jeszcze niższy próg
                mine_mapping = {
                    "energy": "Energy Collector",
                    "gases": "Gas Collector",
                    "minerals": "Mining Complex",
                    "water": "Water Extractor",
                    "organics": "Bio Harvester",
                    "rare_elements": "Rare Element Extractor",
                }
                
                mine_name = mine_mapping.get(best_res)
                if mine_name:
                    factory = BUILDINGS.get(mine_name)
                    if factory:
                        mine = factory()
                        if hex.can_build(mine, planet) and mine.can_afford(planet):
                            return mine
        
        # 3️⃣ Rafinerie
        if B > 3:
            refinery = self.try_pick_refinery(planet, hex)
            if refinery:
                return refinery
        
        # 4️⃣ Population Hub - fallback
        hub = PopulationHub()
        if hex.can_build(hub, planet) and hub.can_afford(planet):
            return hub
        
        return None
    
    def try_pick_refinery(self, planet, hex):
        """Próbuje wybrać rafinerię"""
        
        production = {}
        for h in planet.hex_map.hexes:
            for b in h.buildings_small:
                if hasattr(b, 'resource'):
                    res = b.resource
                    production[res] = production.get(res, 0) + 1
        
        # Smelter
        if (production.get('minerals', 0) >= 2 and 
            production.get('energy', 0) >= 1):
            from buildings.Refinery import Smelter
            smelter = Smelter()
            if hex.can_build(smelter, planet) and smelter.can_afford(planet):
                return smelter
        
        # Chemical Plant
        if (production.get('gases', 0) >= 1 and 
            production.get('water', 0) >= 1):
            from buildings.Refinery import ChemicalPlant
            chem = ChemicalPlant()
            if hex.can_build(chem, planet) and chem.can_afford(planet):
                return chem
        
        return None
    
    def try_transport_resources(self):
        """AI próbuje wyrównać zasoby między planetami"""
        if len(self.empire.planets) < 2:
            return False
        
        resource_planets = {}
        
        for planet in self.empire.planets:
            if not planet.colonized:
                continue
                
            for res, amount in planet.storage.items():
                if res not in resource_planets:
                    resource_planets[res] = []
                resource_planets[res].append((planet, amount))
        
        from core.config import BASIC_RESOURCES
        
        for res in BASIC_RESOURCES:
            if res not in resource_planets:
                continue
                
            planets = resource_planets[res]
            if len(planets) < 2:
                continue
                
            planets.sort(key=lambda x: x[1], reverse=True)
            
            richest_planet, richest_amount = planets[0]
            poorest_planet, poorest_amount = planets[-1]
            
            if richest_amount > 150 and (richest_amount - poorest_amount) > 100:
                cargo = {res: 50.0}
                
                success, msg = self.empire.create_transport(
                    richest_planet,
                    poorest_planet,
                    cargo,
                    "resources"
                )
                
                if success:
                    print(f"[AI {self.empire.name}] Transport: {msg}")
                    return True
        
        return False