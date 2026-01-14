"""
ai/simple_ai.py - AI z systemem ról planet
Planety dostają role na podstawie zasobów i strategii
"""

import random
from buildings.registry import BUILDINGS
from buildings.PopulationHub import PopulationHub
from buildings.SpacePort import SpacePort
from buildings.Mining import MiningComplex
from military.PlanetaryInvasion import PlanetaryInvasion
from military.buildings import Barracks, TrainingGrounds
from core.config import BASIC_RESOURCES, ADVANCED_RESOURCES
import logging

# Simple market prices (cash per unit) used by AI when buying resources
RESOURCE_MARKET_PRICES = {
    # Increased market prices so sells generate meaningful cash
    'energy': 1.0,
    'water': 1.0,
    'minerals': 2.0,
    'organics': 1.2,
    'gases': 0.9,
    'rare_elements': 2.0,
    'alloys': 3.5,
    'chemicals': 2.5,
    'biotech': 4.0,
    'plastics': 1.5,
    'electronics': 5.0,
    'fuel': 2.0,
}
class PlanetRole:
    """Definiuje rolę planety w imperium"""
    MILITARY = "military"        # Baza wojskowa - jednostki + obrona
    METROPOLIS = "metropolis"    # Centrum populacji - huby + zaawansowane budynki
    MINING = "mining"            # Kopalnie podstawowych zasobów
    REFINERY = "refinery"        # Rafinerie - przetwarzanie zasobów
    BALANCED = "balanced"        # Zrównoważona - trochę wszystkiego
    
    @staticmethod
    def get_priority(role):
        """Zwraca priorytety rozwoju dla roli"""
        priorities = {
            PlanetRole.MILITARY: {
                "military_buildings": 10,
                "population": 5,
                "mining": 0,
                "refineries": 1
            },
            PlanetRole.METROPOLIS: {
                "population": 10,
                "refineries": 2,
                "mining": 0,
                "military_buildings": 0
            },
            PlanetRole.MINING: {
                "mining": 10,
                "population": 4,
                "refineries": 3,
                "military_buildings": 0
            },
            PlanetRole.REFINERY: {
                "refineries": 10,
                "mining": 0,
                "population": 0,
                "military_buildings": 0
            },
            PlanetRole.BALANCED: {
                "mining": 5,
                "population": 5,
                "refineries": 4,
                "military_buildings": 3
            }
        }
        return priorities.get(role, priorities[PlanetRole.BALANCED])


class SimpleAI:
    def __init__(self, empire, galaxy):
        self.empire = empire
        self.galaxy = galaxy
        self.cooldown = 10
        self.colonization_cooldown = 1
        self.military_cooldown = 1
        self.attack_cooldown = 1
        
        self.planet_roles = {}  

    def tick(self):
        """Główna pętla AI - z systemem ról"""
        self.cooldown -= 1
        self.colonization_cooldown -= 1
        self.military_cooldown -= 1
        self.attack_cooldown -= 1
    
        if self.cooldown > 0:
            return
        
        self.cooldown = 1
        
        # Aktualizuj role planet
        self.update_planet_roles()
        
        if self.empire.planets:
            for planet in self.empire.planets:
                self.develop_planet(planet)
            
        if self.colonization_cooldown <= 0:
            if self.try_colonize():
                self.colonization_cooldown = 1

        # Przenieś populację z metropolii na planety potrzebujące
        self.try_transfer_population()

        
        self.try_transport_resources()

        
        if self.military_cooldown <= 0:
            if self.handle_military():
                self.military_cooldown = 1

                
        if self.attack_cooldown <= 0:
            self.try_attack()
            self.attack_cooldown = 1

    # ============================================
    # SYSTEM RÓL PLANET
    # ============================================
    
    def update_planet_roles(self):
        """Aktualizuje role wszystkich planet w imperium"""
        if not self.empire.planets:
            return
        
        # Usuń role planet które już nie należą do imperium
        current_ids = {id(p) for p in self.empire.planets}
        self.planet_roles = {
            pid: role for pid, role in self.planet_roles.items()
            if pid in current_ids
        }
        
        # Przypisz role nowym planetom
        for planet in self.empire.planets:
            if not planet.colonized:
                continue
                
            pid = id(planet)
            if pid not in self.planet_roles:
                self.planet_roles[pid] = self.determine_planet_role(planet)

        # Ensure at least one planet is designated MILITARY: pick a suitable candidate
        military_count = sum(1 for pid, roles in self.planet_roles.items() if PlanetRole.MILITARY in (roles if isinstance(roles, list) else [roles]))
        if military_count == 0:
            # Prefer a planet with many hexes (>=10), otherwise the one with largest hex count
            candidates = [p for p in self.empire.planets if p.colonized and hasattr(p, 'hex_map')]
            if candidates:
                # prefer hex_count >= 10
                big = [p for p in candidates if len(p.hex_map.hexes) >= 10]
                pick = None
                if big:
                    # choose the one with largest population among big planets
                    pick = max(big, key=lambda x: (len(x.hex_map.hexes), getattr(x.population, 'size', 0)))
                else:
                    pick = max(candidates, key=lambda x: (len(x.hex_map.hexes), getattr(x.population, 'size', 0)))

                if pick:
                    self.planet_roles[id(pick)] = [PlanetRole.MILITARY]
    
    def determine_planet_role(self, planet):
        """Określa optymalną rolę dla planety na podstawie zasobów"""
        
        # Analiza zasobów
        resource_totals = {}
        for res in BASIC_RESOURCES:
            resource_totals[res] = sum(h.resources.get(res, 0) for h in planet.hex_map.hexes)
        
        total_resources = sum(resource_totals.values())
        
        # Liczba hexów
        hex_count = len(planet.hex_map.hexes)
        
        roles = []

        # 1️⃣ MILITARY - jeśli mało zasobów ale dużo miejsca
        if total_resources < 5 and hex_count >= 10:
            roles.append(PlanetRole.MILITARY)

        # 2️⃣ MINING - jeśli dominują podstawowe zasoby (minerals, energy, gases)
        basic_resources = resource_totals.get('minerals', 0) + \
                         resource_totals.get('energy', 0) + \
                         resource_totals.get('gases', 0)

        if basic_resources > total_resources * 0.5 and total_resources > 6:
            roles.append(PlanetRole.MINING)

        # 3️⃣ REFINERY - jeśli ma różnorodne zasoby do przetwarzania
        diverse_resources = sum(1 for v in resource_totals.values() if v > 1.0)
        if diverse_resources >= 5:
            roles.append(PlanetRole.REFINERY)

        # 4️⃣ METROPOLIS - jeśli jest pierwszą planetą lub ma dużo miejsca
        if len(self.empire.planets) == 1 or hex_count >= 18:
            roles.append(PlanetRole.METROPOLIS)

        # 追加: jeśli już są rafinerie na planecie, uznaj ją też za `refinery`
        refinery_names = {"Smelter", "Chemical Plant", "Bioreactor", "Polymer Factory", "Electronics Fab", "Fuel Refinery"}
        for h in planet.hex_map.hexes:
            if getattr(h, 'building_major', None) and h.building_major.name in refinery_names:
                if PlanetRole.REFINERY not in roles:
                    roles.append(PlanetRole.REFINERY)
            for b in h.buildings_small:
                if b.name in refinery_names and PlanetRole.REFINERY not in roles:
                    roles.append(PlanetRole.REFINERY)

        # Domyślnie zrównoważona, jeśli brak ról
        if not roles:
            roles.append(PlanetRole.BALANCED)

        return roles
    
    def get_planet_role(self, planet):
        """Zwraca rolę planety"""
        r = self.planet_roles.get(id(planet), [PlanetRole.BALANCED])
        # Zwrot kompatybilny: podstawowa (pierwsza) rola
        return r[0] if isinstance(r, list) else r

    def get_planet_roles(self, planet):
        """Zwraca listę ról planety (nowe API)"""
        r = self.planet_roles.get(id(planet), [PlanetRole.BALANCED])
        return r if isinstance(r, list) else [r]

    def can_start_build(self, planet, building):
        """Check if building can start without dropping population below 1 and affordability"""
        # affordability: existing method
        if not building.can_afford(planet):
            # Try to purchase missing resources with cash (AI market) to enable the build
            bought = self._attempt_buy_missing_resources(planet, building)
            if not bought:
                return False

        pop_cost = getattr(building, 'pop_cost', 0.0)
        # If building is a PopulationHub, keep the old safe rule: must keep at least 1 population
        if isinstance(building, PopulationHub):
            if planet.population and (planet.population.size - pop_cost) < 1.0:
                return False

        # For other buildings (refineries, mines, military), allow building down to a small safe floor
        # to enable low-pop colonies to get necessary infrastructure. Avoid decolonization (<= 0.0).
        else:
            MIN_POP_AFTER = 0.25
            if planet.population and (planet.population.size - pop_cost) < MIN_POP_AFTER:
                return False

        return True

    def _attempt_buy_missing_resources(self, planet, building):
        """Try to buy missing resources required by `building.cost` using empire.cash.
        Returns True if purchase was made and now building.can_afford(planet) is True.
        The AI will only buy if it can afford the full missing amount for simplicity."""
        if not hasattr(building, 'cost') or not building.cost:
            return False

        missing = {}
        total_price = 0.0
        for r, req in building.cost.items():
            have = planet.storage.get(r, 0.0)
            need = max(0.0, req - have)
            if need > 0.0:
                price = RESOURCE_MARKET_PRICES.get(r, 1.0)
                missing[r] = need
                total_price += need * price

        if not missing:
            return False

        # Safety: do not spend more than a fraction of empire cash on a single build
        max_spend = max(10.0, self.empire.cash * 0.5)
        if total_price <= 0.0 or total_price > self.empire.cash or total_price > max_spend:
            return False

        # Execute purchase: deduct cash, add resources to planet storage
        self.empire.cash -= total_price
        for r, amt in missing.items():
            planet.storage[r] = planet.storage.get(r, 0.0) + amt

        print(f"[AI {self.empire.name}] Bought resources for build on {getattr(planet,'name',id(planet))}: {missing} cost={total_price:.1f}")

        # Re-check affordability
        return building.can_afford(planet)

    # ============================================
    # MILITARY SYSTEM - z uwzględnieniem roli
    # ============================================
    
    def handle_military(self):
                planet = self.pick_military_planet()
                if not planet:
                    return False

                if planet.military_level < 2:
                    if self.try_build_military_building(planet):
                        logging.info("[AI %s] Built military building on %s", self.empire.name, getattr(planet, 'name', id(planet)))
                        return True

                # try recruit if garrison small
                garrison_size = len(planet.military_manager.garrison)
                max_garrison = 5 + int(planet.military_level * 2)

                if garrison_size < max_garrison:
                    if self.try_recruit_unit(planet):
                        logging.info("[AI %s] Recruiting unit on planet %s", self.empire.name, getattr(planet, 'name', id(planet)))
                        return True

                return False

    def pick_military_planet(self):
                if not self.empire.planets:
                    return None
                candidates = []
                for p in self.empire.planets:
                    if not getattr(p, 'colonized', False) or not getattr(p, 'population', None):
                        continue
                    score = p.population.size * 2 + p.military_level * 10 + len(p.military_manager.garrison) * 5
                    if p.storage.get('alloys', 0) > 50:
                        score += 20
                    candidates.append((p, score))
                if not candidates:
                    return None
                candidates.sort(key=lambda x: -x[1])
                return candidates[0][0]

    def try_build_military_building(self, planet):
                free_hexes = [h for h in planet.hex_map.hexes if not h.is_blocked() or len(h.buildings_small) < planet.hex_cap]
                if not free_hexes:
                    return False
                hex = random.choice(free_hexes)

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
                    logging.info("[AI %s] %s", self.empire.name, msg)
                    return True
                return False

    def try_recruit_unit(self, planet):
                from military.units import get_available_units
                mm = planet.military_manager
                available = get_available_units(planet.military_level)
                if not available:
                    return False
                if planet.military_level < 2:
                    unit_class = available[0]
                elif planet.military_level < 3:
                    unit_class = random.choice(available[:2])
                else:
                    unit_class = random.choice(available)
                can_produce, msg = mm.can_produce(unit_class)
                if not can_produce:
                    return False
                success, msg = mm.start_production(unit_class, doctrine=None)
                if success:
                    logging.info("[AI %s] %s", self.empire.name, msg)
                    return True
                return False

    def try_attack(self):
                if not self.empire.planets:
                    return
                source_planet = max(self.empire.planets, key=lambda p: len(p.military_manager.garrison))
                garrison = source_planet.military_manager.garrison
                if len(garrison) < 3:
                    return
                enemy_planet = self.find_enemy_planet()
                if not enemy_planet:
                    return
                attack_force = garrison[: len(garrison) // 2]
                logging.info("[AI %s] Launching invasion on enemy planet!", self.empire.name)
                logging.info("  Attack force: %d units", len(attack_force))
                for unit in attack_force:
                    garrison.remove(unit)
                invasion = PlanetaryInvasion(self.empire, enemy_planet, attack_force)
                if hasattr(self.galaxy, 'active_invasions'):
                    self.galaxy.active_invasions.append(invasion)

    def find_enemy_planet(self):
                for entry in self.galaxy.systems:
                    for planet in entry["system"].planets:
                        if planet.owner and planet.owner != self.empire:
                            return planet
                return None

    # ============================================
    # DEVELOPMENT SYSTEM - z uwzględnieniem ról
    # ============================================
    
    def develop_planet(self, planet):
        """Rozwija planetę zgodnie z jej rolą"""
        
        hex = self.pick_hex(planet)
        if not hex:
            return
        
        building = self.pick_building(planet, hex)
        if not building:
            return
        
        building.owner = self.empire
        success, msg = building.build(planet, hex)
        
        if success:
            role = self.get_planet_role(planet)
            print(f"[AI {self.empire.name}] Built on {role} planet: {msg}")

    def pick_hex(self, planet):
        """Wybiera najlepszy hex do budowy"""
        free_hexes = [
            h for h in planet.hex_map.hexes
            if (not h.is_blocked() or 
                len(h.buildings_small) < planet.hex_cap)
        ]
        
        if not free_hexes:
            return None
        
        role = self.get_planet_role(planet)
        
        hex_scores = []
        for h in free_hexes:
            score = 0
            
            # Score bazuje na roli
            if role == PlanetRole.MINING:
                # Priorytet: wysokie zasoby podstawowe
                score = h.resources.get('minerals', 0) * 2 + \
                       h.resources.get('energy', 0) * 2 + \
                       h.resources.get('gases', 0) * 1.5
            
            elif role == PlanetRole.REFINERY:
                # Priorytet: różnorodność zasobów
                score = len([v for v in h.resources.values() if v > 0.2])
            
            elif role == PlanetRole.METROPOLIS or role == PlanetRole.MILITARY:
                # Priorytet: puste hexagony (dla budynków specjalnych)
                if not h.buildings_small:
                    score = 10
                else:
                    score = 1
            
            else:  # BALANCED
                score = sum(h.resources.values())
            
            hex_scores.append((h, score))
        
        hex_scores.sort(key=lambda x: -x[1])
        top_count = max(1, len(hex_scores) // 5)
        top_hexes = [h for h, _ in hex_scores[:top_count]]
        
        return random.choice(top_hexes)

    def pick_building(self, planet, hex):
        """Wybiera budynek zgodny z rolą planety"""
        
        role = self.get_planet_role(planet)
        priorities = PlanetRole.get_priority(role)
        
        P = planet.population.size
        B = planet.total_buildings()
        
        # Policz ile mamy kopalń i rafinerii
        mines_count = 0
        refineries_count = 0
        for h in planet.hex_map.hexes:
            for b in h.buildings_small:
                if hasattr(b, 'resource'):  # Kopalnia
                    mines_count += 1
                elif 'Refinery' in b.__class__.__name__ or 'Smelter' in b.__class__.__name__ or \
                     'Plant' in b.__class__.__name__ or 'Bioreactor' in b.__class__.__name__:
                    refineries_count += 1
        
        # 1️⃣ Military buildings - tylko dla MILITARY i METROPOLIS
        if priorities.get("military_buildings", 0) >= 5:
            # Allow building on slightly smaller colonies so AI can establish a military planet
            if planet.military_level < 1 and P > 1:
                barracks = Barracks()
                if hex.can_build(barracks, planet) and self.can_start_build(planet, barracks):
                    return barracks
        
        # 2️⃣ Population Hub - głównie dla METROPOLIS
        population_priority = priorities.get("population", 0)
        
        if population_priority >= 8:
            # Metropolis - build hubs but avoid spamming: only if planet has few buildings
            if B < 4:
                hub = PopulationHub()
                if hex.can_build(hub, planet) and self.can_start_build(planet, hub):
                    return hub
        elif population_priority >= 5:
            # Inne - buduj gdy brakuje populacji
            if B > 5 and P < (B * 0.15):
                hub = PopulationHub()
                if hex.can_build(hub, planet) and self.can_start_build(planet, hub):
                    return hub
        
        # 3️⃣ Refineries - WYSOKI PRIORYTET gdy zasoby i brak rafinerii
        refinery_priority = priorities.get("refineries", 0)

        # Allow building a refinery even if no mines exist yet — decision deferred
        # to `try_pick_refinery` which checks planet resource totals.
        if refinery_priority >= 4:
            # threshold: target at least one refinery, or ~1/3 of mines if mines exist
            threshold = max(1, int(max(1, mines_count) / 3))
            if refineries_count < threshold:
                refinery = self.try_pick_refinery(planet, hex)
                if refinery:
                    if not self.can_start_build(planet, refinery):
                        can_afford = refinery.can_afford(planet)
                        pop_after = (planet.population.size - getattr(refinery, 'pop_cost', 0.0)) if hasattr(planet, 'population') else None
                        print(f"[AI DEBUG {self.empire.name}] Refinery {refinery.name} blocked on {getattr(planet,'name',id(planet))}: can_afford={can_afford}, pop_after={pop_after}")
                    else:
                        print(f"[AI {self.empire.name}] Building refinery on {role} planet (mines={mines_count}, refineries={refineries_count})")
                        return refinery
        
        # 4️⃣ Mining - priorytet dla MINING planet (tylko jeśli nie trzeba rafinerii)
        mining_priority = priorities.get("mining", 0)
        
        if mining_priority >= 5 and hex.resources:
            best_res = max(hex.resources, key=hex.resources.get)
            best_val = hex.resources[best_res]
            
            threshold = 0.1 if mining_priority >= 8 else 0.2
            
            if best_val > threshold:
                mine_name = {
                    "energy": "Energy Collector",
                    "gases": "Gas Collector",
                    "minerals": "Mining Complex",
                    "water": "Water Extractor",
                    "organics": "Bio Harvester",
                    "rare_elements": "Rare Element Extractor",
                }.get(best_res)
                
                if mine_name:
                    factory = BUILDINGS.get(mine_name)
                    if factory:
                        mine = factory()
                        # don't overbuild mines if we lack refineries or pop
                        if mines_count > refineries_count * 3 + 2:
                            pass
                        else:
                            if hex.can_build(mine, planet) and self.can_start_build(planet, mine):
                                return mine
        
        # 5️⃣ Fallback - Population Hub: only build if planet actually needs population
        hub = PopulationHub()
        # Count current hubs on planet
        hub_count = 0
        for h in planet.hex_map.hexes:
            for b in h.buildings_small:
                if b.name == 'Population Hub':
                    hub_count += 1

        pop_need = getattr(planet, 'max_population', 100.0) * 0.6
        if planet.population.size < pop_need and hub_count < 3:
            if hex.can_build(hub, planet) and self.can_start_build(planet, hub):
                return hub
        # Debug: no building chosen
        print(f"[AI DEBUG {self.empire.name}] No building chosen for planet {getattr(planet,'name',id(planet))}: role={role}, P={P}, B={B}, mines={mines_count}, refineries={refineries_count}, priorities={priorities}")
        return None
    
    def try_pick_refinery(self, planet, hex):
        """Próbuje wybrać rafinerię"""
        # Zsumuj zasoby surowców na planecie (hex resources)
        resource_totals = {}
        for h in planet.hex_map.hexes:
            for res, val in h.resources.items():
                resource_totals[res] = resource_totals.get(res, 0.0) + val

        refineries = []

        # Helper: decide if planet has enough raw inputs for a refinery
        def has_inputs(inputs):
            # require that for at least one input resource total >= inputs[res] * 3
            for res, req in inputs.items():
                if resource_totals.get(res, 0.0) >= req * 3:
                    return True
            return False

        # Sprawdź każdy typ rafinerii i dodaj tylko jeśli są surowce
        try:
            from buildings.Refinery import Smelter, ChemicalPlant, Bioreactor, PolymerFactory, ElectronicsFab, FuelRefinery
        except Exception:
            Smelter = ChemicalPlant = Bioreactor = PolymerFactory = ElectronicsFab = FuelRefinery = None

        if Smelter:
            sm = Smelter()
            if has_inputs(sm.inputs) and hex.can_build(sm, planet) and sm.can_afford(planet):
                refineries.append(('Smelter', sm))

        if ChemicalPlant:
            cp = ChemicalPlant()
            if has_inputs(cp.inputs) and hex.can_build(cp, planet) and cp.can_afford(planet):
                refineries.append(('ChemicalPlant', cp))

        if Bioreactor:
            br = Bioreactor()
            if has_inputs(br.inputs) and hex.can_build(br, planet) and br.can_afford(planet):
                refineries.append(('Bioreactor', br))

        # Also consider additional refinery types (polymer, electronics, fuel)
        if PolymerFactory:
            pf = PolymerFactory()
            if has_inputs(getattr(pf, 'inputs', {})) and hex.can_build(pf, planet) and pf.can_afford(planet):
                refineries.append(('PolymerFactory', pf))

        if ElectronicsFab:
            ef = ElectronicsFab()
            if has_inputs(getattr(ef, 'inputs', {})) and hex.can_build(ef, planet) and ef.can_afford(planet):
                refineries.append(('ElectronicsFab', ef))

        if FuelRefinery:
            fr = FuelRefinery()
            if has_inputs(getattr(fr, 'inputs', {})) and hex.can_build(fr, planet) and fr.can_afford(planet):
                refineries.append(('FuelRefinery', fr))

        if refineries:
            name, refinery = random.choice(refineries)
            print(f"[AI {self.empire.name}] Selected {name} (resource_totals: { {k: round(v,1) for k,v in resource_totals.items()} })")
            return refinery

        # Fallback: if no strict-match refineries found, try a relaxed approach.
        # This helps ensure the AI actually builds refineries when needed (so
        # military production can be enabled). We attempt the following:
        #  - allow building when planet shows at least some required inputs
        #  - attempt to buy missing inputs via `_attempt_buy_missing_resources()`
        #    to unblock the build if empire cash permits
        try:
            fallback_candidates = []
            for RefClass, label in ((Smelter, 'Smelter'), (ChemicalPlant, 'ChemicalPlant'), (Bioreactor, 'Bioreactor'), (PolymerFactory, 'PolymerFactory'), (ElectronicsFab, 'ElectronicsFab'), (FuelRefinery, 'FuelRefinery')):
                if not RefClass:
                    continue
                inst = RefClass()
                # must be placeable on this hex
                if not hex.can_build(inst, planet):
                    continue

                # relaxed_has_inputs: at least one of the required inputs present
                relaxed_ok = False
                for res, req in getattr(inst, 'inputs', {}).items():
                    if resource_totals.get(res, 0.0) >= req:
                        relaxed_ok = True
                        break

                # If we have at least some inputs, try to ensure affordability.
                if relaxed_ok:
                    if inst.can_afford(planet):
                        fallback_candidates.append((label, inst))
                    else:
                        # attempt to buy missing inputs to enable the build
                        bought = False
                        try:
                            bought = self._attempt_buy_missing_resources(planet, inst)
                        except Exception:
                            bought = False

                        if bought and inst.can_afford(planet):
                            fallback_candidates.append((label, inst))

            if fallback_candidates:
                name, refinery = random.choice(fallback_candidates)
                print(f"[AI {self.empire.name}] (fallback) Selected {name} (resource_totals: { {k: round(v,1) for k,v in resource_totals.items()} })")
                return refinery
        except Exception:
            # swallow fallback errors to avoid breaking AI tick
            pass

        return None

    # ============================================
    # COLONIZATION SYSTEM
    # ============================================
    
    def try_colonize(self):
        """Próbuje skolonizować nową planetę"""
        valid_sources = []
        for p in self.empire.planets:
            if not p.colonized or not p.population or p.population.size <= 0:
                continue

            if (p.storage.get('energy', 0) >= 8 and 
                p.storage.get('minerals', 0) >= 5 and
                p.population.size >= 1.0):
                valid_sources.append(p)
        
        if not valid_sources:
            return False
        
        source = max(valid_sources, 
                    key=lambda p: p.storage.get('energy', 0) + p.storage.get('minerals', 0))
        
        target = self.find_colonization_target(source)
        if not target:
            return False
        
        # ✅ Ostateczna weryfikacja przed kolonizacją
        if target.owner or target.colonized or target.colonization_state != "none":
            print(f"[AI {self.empire.name}] Target planet already claimed, aborting colonization")
            return False
        
        free_hex = next(
            (h for h in target.hex_map.hexes if not h.is_blocked()),
            None
        )
        if not free_hex:
            free_hex = random.choice(target.hex_map.hexes)
        
        spaceport = SpacePort()
        spaceport.owner = self.empire
        
        success, msg = spaceport.build(target, free_hex, source)
        
        if success:
            print(f"[AI {self.empire.name}] {msg}")
            # Nowa planeta dostanie rolę przy następnym update_planet_roles()
            return True
        else:
            print(f"[AI {self.empire.name}] Colonization failed: {msg}")
        
        return False

    def try_transfer_population(self):
        """Przenosi populację z metropolii do planet potrzebujących populacji (używa transportów)"""
        # Źródła: metropolie z nadmiarem populacji
        sources = [p for p in self.empire.planets if PlanetRole.METROPOLIS in self.get_planet_roles(p) and p.population.size >= 4.0]
        if not sources:
            return False

        # Cele: skolonizowane planety z bardzo niską populacją
        targets = [p for p in self.empire.planets if p.colonized and p.population.size < 1.0 and p.population.size >= 0.0]
        # Usuń źródła z listy potencjalnych celów
        targets = [t for t in targets if t not in sources]
        if not targets:
            return False

        # Wybierz najsilniejszą metropolię i najsłabszą planetę
        source = max(sources, key=lambda p: p.population.size)
        target = min(targets, key=lambda p: p.population.size)

        # Ilość do wysłania: minimalnie 1, maksymalnie 2 albo nadmiar nad 2
        amount = min(2.0, max(1.0, source.population.size - 2.0))
        if amount < 1.0:
            return False

        ok, msg = self.empire.create_transport(source, target, amount, transport_type="population")
        if ok:
            print(f"[AI {self.empire.name}] Transporting pop {amount:.1f} from {id(source)} to {id(target)}")
            return True
        else:
            # fallback: jeśli transport nie powiódł się, spróbuj bezpośredniego przesunięcia (bez transportu)
            if source.population.size >= amount:
                source.population.size -= amount
                target.population.size += amount
                print(f"[AI {self.empire.name}] Direct moved pop {amount:.1f} from {id(source)} to {id(target)} (fallback)")
                return True

        return False

    def find_colonization_target(self, source_planet):
        """Znajduje najlepszą planetę do kolonizacji"""
        source_system = None
        for entry in self.galaxy.systems:
            if any(id(p) == id(source_planet) for p in entry["system"].planets):
                source_system = entry
                break
        
        if not source_system:
            return None
        
        candidates = []
        
        for p in source_system["system"].planets:
            # ✅ Sprawdź że planeta nie ma właściciela I nie jest skolonizowana
            if (p.colonization_state == "none" and 
                p != source_planet and 
                not p.owner and 
                not p.colonized):
                score = self.evaluate_planet_for_colonization(p) * 2
                candidates.append((p, score))
        
        for neighbor in source_system["links"]:
            for p in neighbor["system"].planets:
                # ✅ Sprawdź że planeta nie ma właściciela I nie jest skolonizowana
                if (p.colonization_state == "none" and 
                    not p.owner and 
                    not p.colonized):
                    score = self.evaluate_planet_for_colonization(p)
                    candidates.append((p, score))
        
        if not candidates:
            return None
        
        candidates.sort(key=lambda x: -x[1])
        top_count = max(1, len(candidates) // 3)
        
        return random.choice(candidates[:top_count])[0]

    def evaluate_planet_for_colonization(self, planet):
        """Ocenia wartość planety pod kątem przyszłej roli"""
        resource_totals = {}
        for res in BASIC_RESOURCES:
            resource_totals[res] = sum(h.resources.get(res, 0) for h in planet.hex_map.hexes)
        
        total = sum(resource_totals.values())
        hex_count = len(planet.hex_map.hexes)
        
        # Bonus dla planet które mogą pełnić potrzebne role
        role_counts = {}
        for p in self.empire.planets:
            role = self.get_planet_role(p)
            role_counts[role] = role_counts.get(role, 0) + 1
        
        # Priorytetyzuj brakujące role
        if role_counts.get(PlanetRole.MILITARY, 0) == 0:
            if hex_count >= 10:
                total += 5
        
        if role_counts.get(PlanetRole.MINING, 0) < 2:
            basic = resource_totals.get('minerals', 0) + resource_totals.get('energy', 0)
            if basic > 5:
                total += 3
        
        return total + hex_count * 0.5

    # ============================================
    # TRANSPORT SYSTEM
    # ============================================
    
    def try_transport_resources(self):
        """Transport zasobów między planetami o różnych rolach"""
        if len(self.empire.planets) < 2:
            return False
        # 0) Ensure military planets have alloys: try donors or buy if needed
        # This runs before opportunistic selling so alloy shortfalls are
        # addressed with transfers/purchases first.
        try:
            if self.ensure_military_alloys():
                return True
        except Exception:
            pass

        # 0.5) opportunistic selling: convert large surpluses to cash to fund purchases
        balances = self.evaluate_all_planet_balances()
        if self.sell_surplus_resources(balances):
            return True

        # Empire-level quick fix: scan for critical shortages and fix them first
        if self.check_and_fix_shortages():
            return True

        # Najpierw zbalansuj populację (metropolie -> potrzebujące)
        if self._try_transport_population():
            return True

        # Następnie oceniaj bilanse planet i wykonuj transporty zasobów
        balances = self.evaluate_all_planet_balances()
        # 1) spróbuj wyrównać krytyczne braki (military/alloys dla wojskowych)
        if self.balance_resource_transfers(balances):
            return True

        return False
    
    def _try_transport_population(self):
        """Transport populacji z nadmiarowych planet do potrzebujących"""
        # Źródła: planety z populacją znacznie powyżej 50% cap
        sources = [p for p in self.empire.planets if p.colonized and p.population.size > max(3.0, p.max_population * 0.6)]
        targets = [p for p in self.empire.planets if p.colonized and p.population.size < max(1.0, p.max_population * 0.25)]

        if not sources or not targets:
            return False

        # Pare źródeł i celów - wybierz najbardziej oczywiste
        source = max(sources, key=lambda p: p.population.size)
        target = min(targets, key=lambda p: p.population.size)

        # Ile przenieść: zachowaj co najmniej 2.0 na źródle; nie przekraczaj 25% celu
        max_send = max(1.0, source.population.size - 2.0)
        desired_on_target = max(1.0, target.max_population * 0.25)
        amount = min(max_send, desired_on_target - target.population.size)
        amount = min(amount, 4.0)

        if amount < 1.0:
            return False

        ok, msg = self.empire.create_transport(source, target, amount, transport_type="population")
        if ok:
            print(f"[AI {self.empire.name}] Transporting pop {amount:.1f} from {id(source)} to {id(target)}")
            return True

        # fallback direct move (very rare)
        if source.population.size >= amount:
            source.population.size -= amount
            target.population.size += amount
            print(f"[AI {self.empire.name}] Direct moved pop {amount:.1f} from {id(source)} to {id(target)} (fallback)")
            return True

        return False
    
    def _try_transport_critical_resources(self):
        """Transport zasobów do planet które ich potrzebują"""
        # Deprecated: replaced by balance_resource_transfers
        return False

    def evaluate_all_planet_balances(self):
        """Zwraca słownik z bilansem produkcji/zużycia, potrzeb i nadwyżek dla każdej planety.

        Format:
            { planet: { 'production': {...}, 'needs': {...}, 'surpluses': {...} } }
        """
        balances = {}
        for p in self.empire.planets:
            if not p.colonized:
                continue

            production = p.produce() or {}

            needs = {}
            surpluses = {}

            # Oceń podstawowe i zaawansowane zasoby
            resources_considered = BASIC_RESOURCES + ADVANCED_RESOURCES

            for res in resources_considered:
                prod = production.get(res, 0.0)
                storage = p.storage.get(res, 0.0)

                # Jeśli produkcja jest ujemna → potrzeba importu
                if prod < 0:
                    needs[res] = min(60.0, abs(prod) * 4.0 + max(0.0, 12.0 - storage))
                # Jeśli zapas jest niski → potrzeba budżetowa
                elif storage < 8.0:
                    needs[res] = max(0.0, 12.0 - storage)
                # Jeśli produkcja dodatnia i zapas wysoki → nadwyżka
                elif prod > 1.0 and storage > 20.0:
                    surpluses[res] = min(storage - 10.0, prod * 3.0)

            balances[p] = {
                'production': production,
                'needs': needs,
                'surpluses': surpluses,
            }

        return balances

    def balance_resource_transfers(self, balances):
        """Wykonuje transporty zasobów pomiędzy planetami na podstawie obliczonych bilanów.

        Zwraca True jeśli utworzono transport.
        """
        # Najpierw szukamy krytycznych potrzeb (np. alloys dla planet military)
        # Zbierz wszystkie potrzeby
        needs_by_res = {}
        for p, b in balances.items():
            for res, amt in b['needs'].items():
                needs_by_res.setdefault(res, []).append((p, amt))

        # Spróbuj zaspokoić potrzeby od donorów z surplusem
        for res, need_list in needs_by_res.items():
            # Sortuj potrzeby najbardziej pilne
            need_list.sort(key=lambda x: -x[1])
            for target, need_amt in need_list:
                # znajdź donora
                best_donor = None
                best_amount = 0.0
                for donor, b2 in balances.items():
                    if donor == target:
                        continue
                    available = b2['surpluses'].get(res, 0.0)
                    if available > best_amount:
                        best_amount = available
                        best_donor = donor

                # Allow smaller donors to participate; be more willing to move resources
                if best_donor and best_amount > 0.5:
                    send = min(best_amount, need_amt, 40.0)
                    cargo = {res: send}
                    ok, msg = self.empire.create_transport(best_donor, target, cargo, "resources")
                    if ok:
                        print(f"[AI {self.empire.name}] Transport {send:.1f} {res} from {id(best_donor)} to {id(target)}: {msg}")
                        return True

        # Jeśli brak wyraźnych donorów dla potrzeb, spróbuj przenieść ogólne nadwyżki (energy/minerals)
        for res in ['energy', 'minerals', 'alloys']:
            for donor, b in balances.items():
                amt = b['surpluses'].get(res, 0.0)
                # be more willing to move smaller surpluses
                if amt <= 2.0:
                    continue
                # znajdź target potrzebujący
                targets = [ (t, nb['needs'].get(res,0.0)) for t, nb in balances.items() if nb['needs'].get(res,0.0) > 0 ]
                if not targets:
                    continue
                targets.sort(key=lambda x: -x[1])
                target, need_amt = targets[0]
                send = min(amt, need_amt, 40.0)
                cargo = {res: send}
                ok, msg = self.empire.create_transport(donor, target, cargo, "resources")
                if ok:
                    print(f"[AI {self.empire.name}] General transport {send:.1f} {res} from {id(donor)} to {id(target)}: {msg}")
                    return True

        return False
    
    def _get_critical_needs(self, planet):
        """Zasoby których brakuje"""
        needs = {}
        
        role = self.get_planet_role(planet)
        
        # Różne potrzeby w zależności od roli
        if role == PlanetRole.MILITARY:
            if planet.storage.get('alloys', 0) < 20:
                needs['alloys'] = 30
        
        elif role == PlanetRole.METROPOLIS:
            if planet.storage.get('energy', 0) < 15:
                needs['energy'] = 20
        
        # Ogólne potrzeby budowlane
        can_build = any(
            not h.is_blocked() or len(h.buildings_small) < planet.hex_cap
            for h in planet.hex_map.hexes
        )
        
        if can_build:
            for res in ['energy', 'minerals']:
                if planet.storage.get(res, 0) < 8:
                    needs[res] = 15
        
        return needs

    def ensure_military_alloys(self):
        """Ensure military-role planets have enough alloys: prefer transfers, else buy."""
        for p in self.empire.planets:
            if not p.colonized:
                continue
            if self.get_planet_role(p) != PlanetRole.MILITARY:
                continue

            have = p.storage.get('alloys', 0.0)
            target = 30.0
            if have >= target:
                continue

            need = target - have

            donor = self._find_resource_donor('alloys', need, exclude_planet=p)
            if donor and donor.storage.get('alloys', 0.0) > 5.0:
                available = max(0.0, donor.storage.get('alloys', 0.0) - 5.0)
                send = min(available, need, 100.0)
                if send > 0.5:
                    ok, msg = self.empire.create_transport(donor, p, {'alloys': send}, "resources")
                    if ok:
                        print(f"[AI {self.empire.name}] Transporting {send:.1f} alloys to military planet {getattr(p,'name',id(p))}: {msg}")
                        return True

            # No donor: consider buying alloys directly for the planet
            price = RESOURCE_MARKET_PRICES.get('alloys', 1.0)
            cost = price * need
            max_spend = max(10.0, self.empire.cash * 0.5)
            if cost > 0 and cost <= self.empire.cash and cost <= max_spend:
                self.empire.cash -= cost
                p.storage['alloys'] = p.storage.get('alloys', 0.0) + need
                print(f"[AI {self.empire.name}] Bought quick {need:.1f} alloys for military planet {getattr(p,'name',id(p))} cost={cost:.1f}")
                return True

        return False
    
    def _find_resource_donor(self, resource, min_needed, exclude_planet):
        """Znajduje planetę z nadwyżką zasobu"""
        best_donor = None
        best_amount = 0
        
        for planet in self.empire.planets:
            if planet == exclude_planet or not planet.colonized:
                continue
            
            available = planet.storage.get(resource, 0)
            # More aggressive donor selection: accept moderate surpluses
            if available > best_amount and (
                available > (min_needed + 10) or available > (min_needed * 1.2 + 5)
            ):
                best_donor = planet
                best_amount = available
        
        return best_donor

    def check_and_fix_shortages(self):
        """Quick scan across empire planets for critical shortages (resources or pop)
        and create transports from donors when possible. Returns True if a transport
        was created."""
        # 1) Resource criticals per planet
        for p in self.empire.planets:
            if not p.colonized:
                continue
            needs = self._get_critical_needs(p)
            for res, amt in needs.items():
                donor = self._find_resource_donor(res, amt, exclude_planet=p)
                if donor:
                    # leave a small reserve on donor; be willing to send larger amounts
                    min_reserve = max(5.0, amt * 0.5)
                    available = max(0.0, donor.storage.get(res, 0.0) - min_reserve)
                    send = min(available, amt, 50.0)
                    if send > 0.5:
                        ok, msg = self.empire.create_transport(donor, p, {res: send}, "resources")
                        if ok:
                            print(f"[AI {self.empire.name}] Quick transport {send:.1f} {res} from {id(donor)} to {id(p)}: {msg}")
                            return True
                else:
                    # No donor found: consider buying the missing resource with cash
                    price = RESOURCE_MARKET_PRICES.get(res, 1.0)
                    cost = price * amt
                    max_spend = max(10.0, self.empire.cash * 0.5)
                    if cost > 0 and cost <= self.empire.cash and cost <= max_spend:
                        # perform purchase
                        self.empire.cash -= cost
                        p.storage[res] = p.storage.get(res, 0.0) + amt
                        print(f"[AI {self.empire.name}] Bought quick {amt:.1f} {res} for {getattr(p,'name',id(p))} cost={cost:.1f}")
                        return True

        # 2) Population emergencies: bring at least 1 pop if any colony falls below 1.0
        needy = [q for q in self.empire.planets if q.colonized and q.population.size < 1.0]
        if needy:
            # prefer metropolises or largest sources
            # allow slightly smaller sources to contribute
            sources = [q for q in self.empire.planets if q.colonized and q.population.size > 1.6]
            if sources:
                source = max(sources, key=lambda x: x.population.size)
                target = min(needy, key=lambda x: x.population.size)
                # send up to 3.0 but ensure source remains >= 1.0
                amount = min(3.0, max(1.0, source.population.size - 1.0))
                if source.population.size - amount < 1.0:
                    amount = max(1.0, source.population.size - 1.0)
                ok, msg = self.empire.create_transport(source, target, amount, "population")
                if ok:
                    print(f"[AI {self.empire.name}] Emergency pop transport {amount:.1f} from {id(source)} to {id(target)}: {msg}")
                    return True

        return False

    def sell_surplus_resources(self, balances):
        """Scan planet surpluses and sell obvious excess for cash.

        Returns True if any sale happened.
        """
        sold_any = False
        # Conservative rules: sell only when storage >> keep_amount and empire needs cash
        for p, b in balances.items():
            # only consider colonized planets
            if not p.colonized:
                continue

            # prefer selling basic resources when they exceed a high threshold
            for res, amt in b.get('surpluses', {}).items():
                # only sell larger piles
                if amt < 30.0:
                    continue

                # keep a modest buffer on planet
                keep = max(10.0, amt * 0.2)
                price = RESOURCE_MARKET_PRICES.get(res, 1.0)

                revenue = p.sell_excess(self.empire, res, keep, price)
                if revenue and revenue > 0.0:
                    print(f"[AI {self.empire.name}] Sold {res} from planet {getattr(p,'name',id(p))} revenue={revenue:.1f}")
                    sold_any = True
                    # perform only one sale per tick to keep behavior gradual
                    return True

        return sold_any

