"""
ai/simple_ai.py - FIXED VERSION
AI z pełną obsługą systemu wojskowego
"""

import random
from buildings.registry import BUILDINGS
from buildings.PopulationHub import PopulationHub
from buildings.SpacePort import SpacePort
from buildings.Mining import MiningComplex
from military.PlanetaryInvasion import PlanetaryInvasion
from military.buildings import Barracks, TrainingGrounds

class SimpleAI:
    def __init__(self, empire, galaxy):
        self.empire = empire
        self.galaxy = galaxy
        self.cooldown = 0
        self.colonization_cooldown = 1
        self.military_cooldown = 1
        self.attack_cooldown = 1

    def tick(self):
        """Główna pętla AI - z military"""
        self.cooldown -= 1
        self.colonization_cooldown -= 1
        self.military_cooldown -= 1
        self.attack_cooldown -= 1
    
        if self.cooldown > 0:
            return
        
        self.cooldown = 1
        
        
        if self.empire.planets:
            planet = self.pick_development_planet()
            if planet:
                self.develop_planet(planet)
            
        if self.colonization_cooldown <= 0 :
            if self.try_colonize():
                self.colonization_cooldown = 1
                return
        
        if self.try_transport_resources():
            return
        if self.military_cooldown <= 0:
            if self.handle_military():
                self.military_cooldown = 1
                return
        if self.attack_cooldown <= 0:
            self.try_attack()
            self.attack_cooldown = 1
        


    # ============================================
    # MILITARY SYSTEM
    # ============================================
    
    def handle_military(self):
        """Główna logika wojskowa AI"""
        
        # 1️⃣ Wybierz planetę do rozwoju wojskowego
        planet = self.pick_military_planet()
        if not planet:
            return False
        
        # 2️⃣ Buduj infrastrukturę wojskową
        if planet.military_level < 2:  # Priorytet: buduj Barracks
            if self.try_build_military_building(planet):
                print(f"[AI {self.empire.name}] Built military building on {id(planet)}")
                return True
        
        # 3️⃣ Rekrutuj jednostki
        garrison_size = len(planet.military_manager.garrison)
        max_garrison = 5 + int(planet.military_level * 2)  # Większy level = więcej jednostek
        
        if garrison_size < max_garrison:
            if self.try_recruit_unit(planet):
                print(f"[AI {self.empire.name}] Recruiting unit on planet {id(planet)}")
                return True
        
        return False
    
    def pick_military_planet(self):
        """Wybiera najlepszą planetę do rozwoju wojskowego"""
        if not self.empire.planets:
            return None
        
        candidates = []
        
        for p in self.empire.planets:
            if not p.colonized or not p.population:
                continue
            
            # Score: populacja + military level + garrison
            score = (
                p.population.size * 2 +
                p.military_level * 10 +
                len(p.military_manager.garrison) * 5
            )
            
            # Bonus dla planet z dużymi zasobami
            if p.storage.get('alloys', 0) > 50:
                score += 20
            
            candidates.append((p, score))
        
        if not candidates:
            return None
        
        # Wybierz planetę z najwyższym score (główna baza militarna)
        candidates.sort(key=lambda x: -x[1])
        return candidates[0][0]
    
    def try_build_military_building(self, planet):
        """Próbuje zbudować budynek wojskowy"""
        
        # Znajdź wolny hex
        free_hexes = [
            h for h in planet.hex_map.hexes
            if not h.is_blocked() or len(h.buildings_small) < planet.hex_cap
        ]
        
        if not free_hexes:
            return False
        
        hex = random.choice(free_hexes)
        
        # Wybierz budynek
        building = None
        if planet.military_level < 1:
            building = Barracks()
        elif planet.military_level < 2:
            building = TrainingGrounds()
        else:
            return False
        
        if not building.can_afford(planet):
            return False
        
        building.owner = self.empire
        success, msg = building.build(planet, hex)
        
        if success:
            print(f"[AI {self.empire.name}] {msg}")
            return True
        
        return False
    
    def try_recruit_unit(self, planet):
        """Próbuje zrekrutować jednostkę"""
        from military.units import get_available_units
        
        mm = planet.military_manager
        
        # Pobierz dostępne jednostki
        available = get_available_units(planet.military_level)
        
        if not available:
            return False
        
        # Wybierz jednostkę na podstawie military level
        if planet.military_level < 2:
            # Tylko Infantry
            unit_class = available[0]  # Infantry
        elif planet.military_level < 3:
            # Infantry lub Tank
            unit_class = random.choice(available[:2])
        else:
            # Wszystkie dostępne
            unit_class = random.choice(available)
        
        # Sprawdź czy możemy produkować
        can_produce, msg = mm.can_produce(unit_class)
        
        if not can_produce:
            return False
        
        # Rozpocznij produkcję
        success, msg = mm.start_production(unit_class, doctrine=None)
        
        if success:
            print(f"[AI {self.empire.name}] {msg}")
            return True
        
        return False
    
    
    def try_attack(self):
        """Próbuje zaatakować wrogą planetę"""
        if not self.empire.planets:
            return
        
        # Znajdź swoją planetę z największą armią
        source_planet = max(
            self.empire.planets,
            key=lambda p: len(p.military_manager.garrison)
        )
        
        garrison = source_planet.military_manager.garrison
        
        # Atakuj tylko jeśli masz ≥3 jednostki
        if len(garrison) < 3:
            return
        
        # Znajdź wrogą planetę
        enemy_planet = self.find_enemy_planet()
        if not enemy_planet:
            return
        
        # Wyślij połowę armii
        attack_force = garrison[:len(garrison)//2]
        
        print(f"[AI {self.empire.name}] Launching invasion on enemy planet!")
        print(f"  Attack force: {len(attack_force)} units")
        
        # Usuń z garnizonu
        for unit in attack_force:
            garrison.remove(unit)
        

        invasion = PlanetaryInvasion(self.empire, enemy_planet, attack_force)
        
        # Dodaj do gry
        if hasattr(self.galaxy, 'active_invasions'):
            self.galaxy.active_invasions.append(invasion)
    
    def find_enemy_planet(self):
        """Znajduje wrogą planetę do ataku"""
        for entry in self.galaxy.systems:
            for planet in entry["system"].planets:
                if planet.owner and planet.owner != self.empire:
                    return planet
        return None

    # ============================================
    # COLONIZATION SYSTEM
    # ============================================
    
    def try_colonize(self):
        """Próbuje skolonizować nową planetę"""
        
        
        # 1️⃣ Znajdź valid source planets
        valid_sources = []
        for p in self.empire.planets:
            if not p.colonized or not p.population or p.population.size <= 0:
                continue

            # Sprawdź zasoby dla SpacePort (energy=10, minerals=5)
            if (p.storage.get('energy', 0) >= 8 and 
                p.storage.get('minerals', 0) >= 5 and
                p.population.size >= 1.0):

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
            free_hex = random.choice(target.hex_map.hexes)
        
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
            if any(id(p) == id(source_planet) for p in entry["system"].planets):
                source_system = entry
                break

        
        if not source_system:
            print("[AI] Source system not found for colonization")
            return None

        
        candidates = []
        
        # 1️⃣ Planety w tym samym systemie
        for p in source_system["system"].planets:
            if  p.colonization_state == "none" and p != source_planet:
                score = self.evaluate_planet_resources(p) * 2
                candidates.append((p, score))
        
        # 2️⃣ Planety w sąsiednich systemach
        for neighbor in source_system["links"]:
            for p in neighbor["system"].planets:
                if  p.colonization_state == "none":
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

    # ============================================
    # DEVELOPMENT SYSTEM
    # ============================================
    
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
        
        # 1️⃣ Military buildings - priorytet na początku gry
        if planet.military_level < 1 and planet.population.size > 2:
            try:

                barracks = Barracks()
                if hex.can_build(barracks, planet) and barracks.can_afford(planet):
                    return barracks
            except ImportError:
                pass
        
        # 2️⃣ Population Hub - tylko gdy bardzo mało pop
        if B > 5 and P < (B * 0.15):
            hub = PopulationHub()
            if hex.can_build(hub, planet) and hub.can_afford(planet):
                return hub
        
        # 3️⃣ Kopalnie - główny priorytet
        if hex.resources:
            best_res = max(hex.resources, key=hex.resources.get)
            best_val = hex.resources[best_res]
            
            if best_val > 0.15:
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
        
        # 4️⃣ Rafinerie
        if B > 3:
            refinery = self.try_pick_refinery(planet, hex)
            if refinery:
                return refinery
        
        # 5️⃣ Population Hub - fallback
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
        
        # Wszystkie możliwe rafinerie
        refineries = []
        
        # Smelter
        if production.get('minerals', 0) >= 1 and production.get('energy', 0) >= 1:
            from buildings.Refinery import Smelter
            refineries.append(Smelter())
        
        # Chemical Plant
        if production.get('gases', 0) >= 1 and production.get('water', 0) >= 1:
            from buildings.Refinery import ChemicalPlant
            refineries.append(ChemicalPlant())
        
        # Bioreactor
        if production.get('organics', 0) >= 1 and production.get('water', 0) >= 1:
            from buildings.Refinery import Bioreactor
            refineries.append(Bioreactor())
        
        # Spróbuj każdej
        for refinery in refineries:
            if hex.can_build(refinery, planet) and refinery.can_afford(planet):
                return refinery
        
        return None
    
    # ============================================
    # TRANSPORT SYSTEM
    # ============================================
    
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