"""
military/units.py
Kompletny system jednostek wojskowych
"""

from dataclasses import dataclass
from typing import Optional

# ============================================
# DEFINICJE JEDNOSTEK
# ============================================

@dataclass
class UnitStats:
    """Statystyki jednostki"""
    attack: float
    defense: float
    health: float
    speed: int
    morale:float
    upkeep: float

class MilitaryUnit:
    """Bazowa klasa dla jednostki wojskowej"""
    
    def __init__(self, name, stats, owner=None):
        self.name = name
        self.stats = stats
        self.owner = owner
        self.current_health = stats.health
        self.location = None
        self.experience = 0
        self.status = "idle"
        
    def take_damage(self, damage):
        """Otrzymuje obrażenia"""
        actual_damage = max(0, damage - self.stats.defense * 0.1)
        self.current_health -= actual_damage
        return self.current_health <= 0
        
    def heal(self, amount):
        """Leczy jednostkę"""
        self.current_health = min(self.stats.health, self.current_health + amount)
        
    def add_experience(self, xp):
        """Dodaje doświadczenie"""
        self.experience = min(100, self.experience + xp)
        
    def get_rank(self):
        """Zwraca rangę na podstawie doświadczenia"""
        if self.experience < 20:
            return "Recruit"
        elif self.experience < 50:
            return "Veteran"
        elif self.experience < 80:
            return "Elite"
        else:
            return "Legendary"
            
    def combat_power(self):
        """Oblicza siłę bojową (z bonusem za doświadczenie)"""
        exp_bonus = 1.0 + (self.experience / 100) * 0.5
        health_factor = self.current_health / self.stats.health
        return self.stats.attack * exp_bonus * health_factor


# ============================================
# TYPY JEDNOSTEK
# ============================================

class Infantry(MilitaryUnit):
    """Piechota - podstawowa jednostka lądowa"""
    def __init__(self, owner=None):
        stats = UnitStats(
            attack=10.0,
            defense=8.0,
            health=50.0,
            speed=2,
            upkeep=0.5
        )
        super().__init__("Infantry", stats, owner)
        self.production_cost = {
            "minerals": 20,
            "alloys": 5,
            "organics": 10
        }
        self.production_time = 3

class Tank(MilitaryUnit):
    """Czołg - ciężka jednostka pancerna"""
    def __init__(self, owner=None):
        stats = UnitStats(
            attack=25.0,
            defense=20.0,
            health=100.0,
            speed=1,
            upkeep=1.5
        )
        super().__init__("Tank", stats, owner)
        self.production_cost = {
            "minerals": 50,
            "alloys": 30,
            "fuel": 10
        }
        self.production_time = 6

class Fighter(MilitaryUnit):
    """Myśliwiec - jednostka powietrzna"""
    def __init__(self, owner=None):
        stats = UnitStats(
            attack=20.0,
            defense=5.0,
            health=40.0,
            speed=5,
            upkeep=1.0
        )
        super().__init__("Fighter", stats, owner)
        self.production_cost = {
            "alloys": 25,
            "electronics": 15,
            "fuel": 20
        }
        self.production_time = 4

class Frigate(MilitaryUnit):
    """Fregata - mała jednostka kosmiczna"""
    def __init__(self, owner=None):
        stats = UnitStats(
            attack=30.0,
            defense=15.0,
            health=120.0,
            speed=3,
            upkeep=2.0
        )
        super().__init__("Frigate", stats, owner)
        self.production_cost = {
            "alloys": 60,
            "electronics": 30,
            "fuel": 25,
            "rare_elements": 10
        }
        self.production_time = 8
        self.can_travel_systems = True

class Destroyer(MilitaryUnit):
    """Niszczyciel - duża jednostka kosmiczna"""
    def __init__(self, owner=None):
        stats = UnitStats(
            attack=60.0,
            defense=35.0,
            health=250.0,
            speed=2,
            upkeep=4.0
        )
        super().__init__("Destroyer", stats, owner)
        self.production_cost = {
            "alloys": 120,
            "electronics": 60,
            "fuel": 50,
            "rare_elements": 25
        }
        self.production_time = 12
        self.can_travel_systems = True


# ============================================
# KOLEJKA PRODUKCJI
# ============================================

class ProductionQueue:
    """Kolejka produkcji jednostek na planecie"""
    
    def __init__(self):
        self.queue = []
        
    def add_to_queue(self, unit_class, doctrine=None):
        """Dodaje jednostkę do kolejki z opcjonalną doktryną"""
        unit_instance = unit_class()
        self.queue.append({
            "unit_class": unit_class,
            "doctrine": doctrine,
            "progress": 0,
            "time_total": unit_instance.production_time,
            "cost": unit_instance.production_cost
        })
        
    def tick(self, planet):
        """Aktualizuje produkcję co turę"""
        if not self.queue:
            return []
            
        completed = []
        current = self.queue[0]
        
        speed_multiplier = getattr(planet, 'production_speed', 1.0)
        current["progress"] += speed_multiplier
        
        if current["progress"] >= current["time_total"]:
            unit = current["unit_class"](owner=planet.owner)
            unit.location = (planet, None)
            
            # Aplikuj bonusy populacji
            try:
                from military.population_synergy import apply_population_bonuses_to_unit
                apply_population_bonuses_to_unit(unit, planet)
            except ImportError:
                pass  # Jeszcze nie zaimplementowane
            
            # Aplikuj doktrynę
            if current["doctrine"]:
                try:
                    from military.doctrines import apply_doctrine_to_unit
                    apply_doctrine_to_unit(unit, current["doctrine"])
                except ImportError:
                    pass  # Jeszcze nie zaimplementowane
            
            completed.append(unit)
            self.queue.pop(0)
            
        return completed
        
    def cancel_current(self, planet):
        """Anuluje obecną produkcję i zwraca 50% zasobów"""
        if not self.queue:
            return False
            
        current = self.queue.pop(0)
        
        for res, amount in current["cost"].items():
            refund = amount * 0.5
            planet.storage[res] = planet.storage.get(res, 0) + refund
            
        return True
        
    def get_eta(self):
        """Zwraca szacowany czas do ukończenia"""
        if not self.queue:
            return 0
            
        current = self.queue[0]
        remaining = current["time_total"] - current["progress"]
        return max(1, int(remaining))


# ============================================
# MILITARY MANAGER (dla planety)
# ============================================

class PlanetMilitaryManager:
    """Zarządza wojskiem na pojedynczej planecie"""
    
    def __init__(self, planet):
        self.planet = planet
        self.production_queue = ProductionQueue()
        self.garrison = []
        self.production_speed = 1.0
        
    def can_produce(self, unit_class):
        """Sprawdza czy planeta może produkować daną jednostkę"""
        unit = unit_class()
        
        for res, amount in unit.production_cost.items():
            if self.planet.storage.get(res, 0) < amount:
                return False, f"Not enough {res}"
                
        return True, "OK"
        
    def start_production(self, unit_class, doctrine=None):
        """Rozpoczyna produkcję jednostki z opcjonalną doktryną"""
        can_produce, msg = self.can_produce(unit_class)
        
        if not can_produce:
            return False, msg
        
        # Odejmij bazowy koszt jednostki
        unit = unit_class()
        for res, amount in unit.production_cost.items():
            self.planet.storage[res] -= amount
        
        # Odejmij koszt doktryny
        if doctrine:
            for res, amount in doctrine.cost.items():
                if self.planet.storage.get(res, 0) < amount:
                    # Zwróć bazowy koszt
                    for r, a in unit.production_cost.items():
                        self.planet.storage[r] += a
                    return False, f"Not enough {res} for doctrine"
                
                self.planet.storage[res] -= amount
        
        self.production_queue.add_to_queue(unit_class, doctrine)
        
        doc_name = doctrine.name if doctrine else "Standard"
        return True, f"{unit.name} ({doc_name}) production started"
        
    def tick(self):
        """Aktualizacja co turę"""
        completed_units = self.production_queue.tick(self.planet)
        
        for unit in completed_units:
            self.garrison.append(unit)
            print(f"[{self.planet.owner.name}] {unit.name} completed!")
            
        # Upkeep jednostek
        total_upkeep = sum(u.stats.upkeep for u in self.garrison)
        self.planet.owner.energy -= total_upkeep
        
        # Heal jednostki w garnizonie (10% hp per turn)
        for unit in self.garrison:
            unit.heal(unit.stats.health * 0.1)
            
    def get_garrison_strength(self):
        """Zwraca łączną siłę garnizonu"""
        return sum(u.combat_power() for u in self.garrison)


# ============================================
# EMPIRE MILITARY MANAGER
# ============================================

class EmpireMilitaryManager:
    """Zarządza całym wojskiem imperium"""
    
    def __init__(self, empire):
        self.empire = empire
        self.fleets = []
        
    def tick(self):
        """Aktualizacja wszystkich jednostek"""
        for planet in self.empire.planets:
            if hasattr(planet, 'military_manager'):
                planet.military_manager.tick()
                
    def get_total_military_power(self):
        """Zwraca całkowitą siłę wojskową imperium"""
        total = 0
        
        for planet in self.empire.planets:
            if hasattr(planet, 'military_manager'):
                total += planet.military_manager.get_garrison_strength()
                
        return total
        
    def get_unit_count(self):
        """Zwraca liczbę jednostek w imperium"""
        count = 0
        
        for planet in self.empire.planets:
            if hasattr(planet, 'military_manager'):
                count += len(planet.military_manager.garrison)
                
        return count


# ============================================
# REGISTRY JEDNOSTEK
# ============================================

UNIT_TYPES = {
    "Infantry": Infantry,
    "Tank": Tank,
    "Fighter": Fighter,
    "Frigate": Frigate,
    "Destroyer": Destroyer,
}

def get_available_units(planet):
    """Zwraca listę jednostek dostępnych do produkcji na planecie"""
    available = []
    
    # Sprawdź poziom Military
    military_level = 3
    if hasattr(planet, 'strategic_manager'):
        military_res = planet.strategic_manager.resources.get('military')
        if military_res:
            military_level = military_res.level
            
    if military_level == 0:
        return []
        
    # Level 1: Infantry
    if military_level >= 1:
        available.append(Infantry)
        
    # Level 2: Tank, Fighter
    if military_level >= 2:
        available.append(Tank)
        available.append(Fighter)
        
    # Level 3: Frigate
    if military_level >= 3:
        available.append(Frigate)
        
    # Level 4+: Destroyer
    if military_level >= 4:
        available.append(Destroyer)
        
    return available