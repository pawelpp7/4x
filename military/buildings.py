"""
buildings/military_buildings.py
Budynki wojskowe - produkcja, ulepszanie, training
"""

from buildings.Building import Building
from buildings.constants import BUILDING_SMALL, BUILDING_MAJOR, BUILDING_PLANET_UNIQUE

# ============================================
# TIER 1: BASIC MILITARY
# ============================================

class Barracks(Building):
    """
    Podstawowy budynek wojskowy
    - Umożliwia produkcję Infantry
    - +0.5 Military Level
    - +10% morale dla garnizonu
    """
    def __init__(self):
        super().__init__(
            name="Barracks",
            category=BUILDING_SMALL,
            cost={
                "minerals": 30,
                "alloys": 15,
                "organics": 20
            },
            pop_upkeep=0.3,
            cash=-0.5
        )
    
    def apply_planet_effect(self, planet):
        """Zwiększa military level i morale"""
        if not hasattr(planet, 'military_level'):
            planet.military_level = 0
        
        planet.military_level += 0.5
        
        # Bonus morale dla wszystkich jednostek w garnizonie
        if hasattr(planet, 'military_manager'):
            for unit in planet.military_manager.garrison:
                unit.stats.morale = min(1.5, unit.stats.morale + 0.1)


class ArmoryDepot(Building):
    """
    Skład broni
    - -20% koszt produkcji jednostek
    - +5% ATK dla garnizonu
    """
    def __init__(self):
        super().__init__(
            name="Armory Depot",
            category=BUILDING_SMALL,
            cost={
                "minerals": 40,
                "alloys": 25,
                "electronics": 10
            },
            pop_upkeep=0.2,
            cash=-0.4
        )
    
    def apply_planet_effect(self, planet):
        """Redukuje koszty i zwiększa attack"""
        if not hasattr(planet, 'production_cost_modifier'):
            planet.production_cost_modifier = 1.0
        
        planet.production_cost_modifier *= 0.8  # -20%
        
        # Bonus ATK
        if hasattr(planet, 'military_manager'):
            for unit in planet.military_manager.garrison:
                unit.stats.attack *= 1.05


# ============================================
# TIER 2: ADVANCED MILITARY
# ============================================

class VehicleFactory(Building):
    """
    Fabryka pojazdów
    - Umożliwia produkcję Tank
    - +1.0 Military Level
    - +15% production speed
    """
    def __init__(self):
        super().__init__(
            name="Vehicle Factory",
            category=BUILDING_MAJOR,
            cost={
                "minerals": 80,
                "alloys": 50,
                "electronics": 30,
                "fuel": 20
            },
            pop_upkeep=0.8,
            cash=-1.5
        )
    
    def apply_planet_effect(self, planet):
        """Zwiększa military level i production speed"""
        if not hasattr(planet, 'military_level'):
            planet.military_level = 0
        
        planet.military_level += 1.0
        
        if hasattr(planet, 'military_manager'):
            planet.military_manager.production_speed *= 1.15


class AirBase(Building):
    """
    Baza lotnicza
    - Umożliwia produkcję Fighter
    - +1.0 Military Level
    - +20% Speed dla wszystkich jednostek
    """
    def __init__(self):
        super().__init__(
            name="Air Base",
            category=BUILDING_MAJOR,
            cost={
                "alloys": 70,
                "electronics": 40,
                "fuel": 30
            },
            pop_upkeep=0.6,
            cash=-1.2
        )
    
    def apply_planet_effect(self, planet):
        """Zwiększa military level i speed"""
        if not hasattr(planet, 'military_level'):
            planet.military_level = 0
        
        planet.military_level += 1.0
        
        # Bonus speed
        if hasattr(planet, 'military_manager'):
            for unit in planet.military_manager.garrison:
                unit.stats.speed = int(unit.stats.speed * 1.2)


# ============================================
# TIER 3: SPACE MILITARY
# ============================================

class Shipyard(Building):
    """
    Stocznia kosmiczna
    - Umożliwia produkcję Frigate, Destroyer
    - +2.0 Military Level
    - Tylko 1 na planetę
    """
    def __init__(self):
        super().__init__(
            name="Shipyard",
            category=BUILDING_PLANET_UNIQUE,
            cost={
                "alloys": 150,
                "electronics": 80,
                "rare_elements": 40,
                "fuel": 50
            },
            pop_upkeep=1.5,
            cash=-3.0
        )
    
    def apply_planet_effect(self, planet):
        """Umożliwia produkcję statków kosmicznych"""
        if not hasattr(planet, 'military_level'):
            planet.military_level = 0
        
        planet.military_level += 2.0
        planet.has_shipyard = True
    
    def limit_key(self):
        """Tylko 1 Shipyard na planetę"""
        return "shipyard"


# ============================================
# TIER 4: TRAINING & UPGRADES
# ============================================

class TrainingGrounds(Building):
    """
    Poligon treningowy
    - Nowe jednostki startują z 30 XP (Veteran)
    - +15% morale dla garnizonu
    - +10% HP regeneration
    """
    def __init__(self):
        super().__init__(
            name="Training Grounds",
            category=BUILDING_SMALL,
            cost={
                "minerals": 50,
                "alloys": 30,
                "organics": 25
            },
            pop_upkeep=0.4,
            cash=-0.6
        )
    
    def apply_planet_effect(self, planet):
        """Jednostki startują jako veterani"""
        if not hasattr(planet, 'starting_experience'):
            planet.starting_experience = 0
        
        planet.starting_experience += 30
        
        # Bonus morale i regeneracja
        if hasattr(planet, 'military_manager'):
            for unit in planet.military_manager.garrison:
                unit.stats.morale = min(1.5, unit.stats.morale + 0.15)
            
            planet.military_manager.healing_rate = 0.2  # +20% healing


class CommandCenter(Building):
    """
    Centrum dowodzenia
    - +1.5 Military Level
    - -30% upkeep wszystkich jednostek
    - +25% Defense dla garnizonu
    - Tylko 1 na planetę
    """
    def __init__(self):
        super().__init__(
            name="Command Center",
            category=BUILDING_PLANET_UNIQUE,
            cost={
                "alloys": 100,
                "electronics": 60,
                "rare_elements": 30
            },
            pop_upkeep=0.8,
            cash=-1.0
        )
    
    def apply_planet_effect(self, planet):
        """Zmniejsza upkeep i zwiększa defense"""
        if not hasattr(planet, 'military_level'):
            planet.military_level = 0
        
        planet.military_level += 1.5
        
        if hasattr(planet, 'military_manager'):
            # Redukcja upkeep
            for unit in planet.military_manager.garrison:
                unit.stats.upkeep *= 0.7  # -30%
                unit.stats.defense *= 1.25  # +25%
    
    def limit_key(self):
        return "command_center"


class WarAcademy(Building):
    """
    Akademia wojenna
    - Nowe jednostki startują z 60 XP (Elite)
    - Umożliwia produkcję z doktryną
    - +20% do wszystkich statów nowych jednostek
    - Tylko 1 na planetę
    """
    def __init__(self):
        super().__init__(
            name="War Academy",
            category=BUILDING_PLANET_UNIQUE,
            cost={
                "alloys": 120,
                "electronics": 80,
                "biotech": 40,
                "rare_elements": 50
            },
            pop_upkeep=1.0,
            cash=-1.5
        )
    
    def apply_planet_effect(self, planet):
        """Elitarne szkolenie jednostek"""
        if not hasattr(planet, 'starting_experience'):
            planet.starting_experience = 0
        
        planet.starting_experience += 60  # Elite rank
        planet.can_use_doctrines = True
        
        # Bonus do bazowych statów
        if not hasattr(planet, 'unit_stat_bonus'):
            planet.unit_stat_bonus = 1.0
        
        planet.unit_stat_bonus *= 1.20  # +20% wszystkie staty
    
    def limit_key(self):
        return "war_academy"


# ============================================
# TIER 5: PLANETARY DEFENSE
# ============================================

class PlanetaryShield(Building):
    """
    Tarcza planetarna
    - Zmniejsza damage podczas inwazji o 40%
    - +50% Defense dla garnizonu
    - Regeneruje HP tarcz co turę
    """
    def __init__(self):
        super().__init__(
            name="Planetary Shield",
            category=BUILDING_PLANET_UNIQUE,
            cost={
                "alloys": 200,
                "electronics": 150,
                "rare_elements": 80,
                "fuel": 60
            },
            pop_upkeep=0.5,
            cash=-4.0
        )
    
    def apply_planet_effect(self, planet):
        """Aktywuje tarczę planetarną"""
        planet.has_planetary_shield = True
        planet.shield_strength = 1000.0  # HP tarcz
        planet.shield_max = 1000.0
        planet.shield_regen = 50.0  # per turn
        
        # Bonus defense
        if hasattr(planet, 'military_manager'):
            for unit in planet.military_manager.garrison:
                unit.stats.defense *= 1.50
    
    def limit_key(self):
        return "planetary_shield"


class OrbitalDefensePlatform(Building):
    """
    Platforma obrony orbitalnej
    - Automatycznie atakuje atakujące floty
    - 100 ATK, 200 HP
    - Regeneruje 20 HP/turn
    """
    def __init__(self):
        super().__init__(
            name="Orbital Defense Platform",
            category=BUILDING_MAJOR,
            cost={
                "alloys": 150,
                "electronics": 100,
                "rare_elements": 60,
                "fuel": 40
            },
            pop_upkeep=0.3,
            cash=-2.5
        )
    
    def apply_planet_effect(self, planet):
        """Dodaje stacjonarną platformę obronną"""
        if not hasattr(planet, 'orbital_platforms'):
            planet.orbital_platforms = []
        
        platform = {
            "attack": 100.0,
            "health": 200.0,
            "max_health": 200.0,
            "regen": 20.0
        }
        
        planet.orbital_platforms.append(platform)


# ============================================
# SUPPORT BUILDINGS
# ============================================

class MedicalStation(Building):
    """
    Stacja medyczna
    - +50% healing rate
    - Jednostki regenerują 25% HP/turn
    - +10% max HP dla wszystkich jednostek
    """
    def __init__(self):
        super().__init__(
            name="Medical Station",
            category=BUILDING_SMALL,
            cost={
                "biotech": 50,
                "electronics": 30,
                "organics": 40
            },
            pop_upkeep=0.5,
            cash=-0.8
        )
    
    def apply_planet_effect(self, planet):
        """Zwiększa healing"""
        if hasattr(planet, 'military_manager'):
            planet.military_manager.healing_rate = getattr(
                planet.military_manager, 'healing_rate', 0.1
            ) + 0.15  # +15% more healing
            
            for unit in planet.military_manager.garrison:
                unit.stats.health *= 1.10  


class RecruitmentOffice(Building):
    """
    Biuro rekrutacyjne
    - -15% production time
    - -10% production cost
    - +5% morale nowych jednostek
    """
    def __init__(self):
        super().__init__(
            name="Recruitment Office",
            category=BUILDING_SMALL,
            cost={
                "minerals": 40,
                "organics": 30,
                "plastics": 20
            },
            pop_upkeep=0.3,
            cash=-0.4
        )
    
    def apply_planet_effect(self, planet):
        """Przyspiesza rekrutację"""
        if hasattr(planet, 'military_manager'):
            planet.military_manager.production_speed *= 1.18  # ~-15% time
        
        if not hasattr(planet, 'production_cost_modifier'):
            planet.production_cost_modifier = 1.0
        
        planet.production_cost_modifier *= 0.90  # -10% cost
        
        if not hasattr(planet, 'starting_morale_bonus'):
            planet.starting_morale_bonus = 0.0
        
        planet.starting_morale_bonus += 0.05


# ============================================
# MORALE BUILDINGS
# ============================================

class MonumentOfVictory(Building):
    """
    Pomnik zwycięstwa
    - +30% morale dla garnizonu
    - +10% attack
    - Immunity to morale break (morale floor = 0.2)
    """
    def __init__(self):
        super().__init__(
            name="Monument of Victory",
            category=BUILDING_MAJOR,
            cost={
                "minerals": 100,
                "alloys": 60,
                "plastics": 40
            },
            pop_upkeep=0.2,
            cash=-0.5
        )
    
    def apply_planet_effect(self, planet):
        """Inspiruje jednostki"""
        if hasattr(planet, 'military_manager'):
            for unit in planet.military_manager.garrison:
                unit.stats.morale = min(1.5, unit.stats.morale + 0.30)
                unit.stats.attack *= 1.10
            
            # Morale nie może spaść poniżej 0.2
            planet.morale_floor = 0.2


class PropagandaCenter(Building):
    """
    Centrum propagandy
    - +20% morale dla garnizonu
    - +10% morale per turn (regeneracja)
    - Reduces enemy morale by 5% during defense
    """
    def __init__(self):
        super().__init__(
            name="Propaganda Center",
            category=BUILDING_SMALL,
            cost={
                "plastics": 30,
                "electronics": 25,
                "biotech": 20
            },
            pop_upkeep=0.4,
            cash=-0.6
        )
    
    def apply_planet_effect(self, planet):
        """Morale regeneration"""
        if hasattr(planet, 'military_manager'):
            for unit in planet.military_manager.garrison:
                unit.stats.morale = min(1.5, unit.stats.morale + 0.20)
            
            planet.morale_regen = getattr(planet, 'morale_regen', 0.0) + 0.10


# ============================================
# REGISTRY
# ============================================

MILITARY_BUILDINGS = {
    # Tier 1
    "Barracks": lambda: Barracks(),
    "Armory Depot": lambda: ArmoryDepot(),
    
    # Tier 2
    "Vehicle Factory": lambda: VehicleFactory(),
    "Air Base": lambda: AirBase(),
    
    # Tier 3
    "Shipyard": lambda: Shipyard(),
    
    # Tier 4
    "Training Grounds": lambda: TrainingGrounds(),
    "Command Center": lambda: CommandCenter(),
    "War Academy": lambda: WarAcademy(),
    
    # Tier 5
    "Planetary Shield": lambda: PlanetaryShield(),
    "Orbital Defense Platform": lambda: OrbitalDefensePlatform(),
    
    # Support
    "Medical Station": lambda: MedicalStation(),
    "Recruitment Office": lambda: RecruitmentOffice(),
    
    # Morale
    "Monument of Victory": lambda: MonumentOfVictory(),
    "Propaganda Center": lambda: PropagandaCenter(),
}


def get_available_military_buildings(planet):
    """
    Zwraca listę budynków wojskowych dostępnych na planecie
    
    Args:
        planet: Planet object
    
    Returns:
        list: Dostępne budynki wojskowe
    """
    available = []
    
    military_level = getattr(planet, 'military_level', 0)
    
    # Tier 1 (Military Level 0+)
    if military_level >= 0:
        available.extend([
            Barracks(),
            ArmoryDepot(),
            RecruitmentOffice(),
            PropagandaCenter()
        ])
    
    # Tier 2 (Military Level 1+)
    if military_level >= 1:
        available.extend([
            VehicleFactory(),
            TrainingGrounds(),
            MedicalStation()
        ])
    
    # Tier 3 (Military Level 2+)
    if military_level >= 2:
        available.extend([
            AirBase(),
            CommandCenter(),
            MonumentOfVictory()
        ])
    
    # Tier 4 (Military Level 3+)
    if military_level >= 3:
        available.extend([
            Shipyard(),
            WarAcademy(),
            OrbitalDefensePlatform()
        ])
    
    # Tier 5 (Military Level 4+)
    if military_level >= 4:
        available.append(PlanetaryShield())
    
    return available