"""
military/doctrines.py
System doktryn - specjalizacje jednostek oparte na zasobach strategicznych
"""

from dataclasses import dataclass
from typing import Optional, Dict

# ============================================
# DEFINICJA DOKTRYNY
# ============================================

@dataclass
class DoctrineEffect:
    """Efekt doktryny na jednostkę"""
    stat_modifiers: Dict[str, float]  # np. {"attack": 1.2, "defense": 1.1}
    special_ability: Optional[str]    # nazwa specjalnej zdolności
    passive_production: Optional[Dict[str, float]]  # co produkuje per turn
    description: str

class Doctrine:
    """Bazowa klasa doktryny"""
    
    def __init__(self, name, strategic_resource, required_level, icon):
        self.name = name
        self.strategic_resource = strategic_resource  # authority, faith, culture, etc.
        self.required_level = required_level  # min level zasobu strategicznego
        self.icon = icon
        self.cost = {}  # dodatkowy koszt przy rekrutacji
        
    def can_apply(self, planet):
        """Sprawdza czy planeta może zastosować doktrynę"""
        if not hasattr(planet, 'strategic_manager'):
            return False
        
        # ✅ ZMIANA: Planety z Military Level 3+ mogą używać WSZYSTKICH doktryn
        military_res = planet.strategic_manager.resources.get('military')
        if military_res and military_res.level >= 3:
            # Military planet unlocks all doctrines regardless of other resources
            return True
            
        resource = planet.strategic_manager.resources.get(self.strategic_resource)
        if not resource:
            return False
            
        return resource.level >= self.required_level
        
    def get_effect(self):
        """Zwraca efekt doktryny"""
        return DoctrineEffect(
            stat_modifiers={},
            special_ability=None,
            passive_production=None,
            description=""
        )
        
    def apply_to_unit(self, unit):
        """Aplikuje doktrynę do jednostki"""
        effect = self.get_effect()
        
        # Modyfikatory statystyk
        for stat, multiplier in effect.stat_modifiers.items():
            if hasattr(unit.stats, stat):
                current = getattr(unit.stats, stat)
                setattr(unit.stats, stat, current * multiplier)
        
        # Zdolności specjalne
        unit.doctrine = self
        unit.special_ability = effect.special_ability
        unit.passive_production = effect.passive_production or {}


# ============================================
# MILITARY DOCTRINES (stat buffs)
# ============================================

class ShockTrooperDoctrine(Doctrine):
    """
    Military Level 2 - Shock Trooper
    Agresywna doktryna: +40% ATK, -10% DEF, +20% Speed
    """
    def __init__(self):
        super().__init__(
            name="Shock Trooper",
            strategic_resource="military",
            required_level=2,
            icon="⚡"
        )
        self.cost = {"alloys": 5}
        
    def get_effect(self):
        return DoctrineEffect(
            stat_modifiers={
                "attack": 1.40,
                "defense": 0.90,
                "speed": 1.20
            },
            special_ability="blitz_attack",
            passive_production=None,
            description="Aggressive assault unit. +40% ATK, -10% DEF, +20% Speed. Special: First strike in combat."
        )


class FortifiedDoctrine(Doctrine):
    """
    Military Level 3 - Fortified
    Defensywna doktryna: -20% ATK, +60% DEF, +40% HP
    """
    def __init__(self):
        super().__init__(
            name="Fortified",
            strategic_resource="military",
            required_level=3,
            icon="🛡️"
        )
        self.cost = {"alloys": 8}
        
    def get_effect(self):
        return DoctrineEffect(
            stat_modifiers={
                "attack": 0.80,
                "defense": 1.60,
                "health": 1.40
            },
            special_ability="entrench",
            passive_production=None,
            description="Defensive position unit. -20% ATK, +60% DEF, +40% HP. Special: Takes 50% less damage when defending."
        )


class EliteGuardDoctrine(Doctrine):
    """
    Military Level 4 - Elite Guard
    Zbalansowana doktryna: +25% all stats, +50% starting XP
    """
    def __init__(self):
        super().__init__(
            name="Elite Guard",
            strategic_resource="military",
            required_level=4,
            icon="⭐"
        )
        self.cost = {"alloys": 12, "rare_elements": 3}
        
    def get_effect(self):
        return DoctrineEffect(
            stat_modifiers={
                "attack": 1.25,
                "defense": 1.25,
                "health": 1.25,
                "speed": 1.25
            },
            special_ability="veteran_training",
            passive_production=None,
            description="Elite professional unit. +25% all stats. Starts with 50 XP (Veteran rank)."
        )


# ============================================
# SCIENCE DOCTRINES (research & efficiency)
# ============================================

class TechnicianDoctrine(Doctrine):
    """
    Science Level 2 - Technician
    Produkuje science points podczas stacjonowania
    """
    def __init__(self):
        super().__init__(
            name="Technician",
            strategic_resource="science",
            required_level=2,
            icon="🔬"
        )
        self.cost = {"electronics": 10}
        
    def get_effect(self):
        return DoctrineEffect(
            stat_modifiers={
                "defense": 1.10  # lekka obrona
            },
            special_ability="field_research",
            passive_production={
                "science_points": 0.5  # nowy zasób strategiczny
            },
            description="Research-focused unit. Generates 0.5 science points/turn when garrisoned. +10% DEF."
        )


class EngineerCorpsDoctrine(Doctrine):
    """
    Science Level 3 - Engineer Corps
    Przyspiesza budowę budynków na planecie
    """
    def __init__(self):
        super().__init__(
            name="Engineer Corps",
            strategic_resource="science",
            required_level=3,
            icon="🔧"
        )
        self.cost = {"electronics": 15, "alloys": 5}
        
    def get_effect(self):
        return DoctrineEffect(
            stat_modifiers={
                "defense": 1.15
            },
            special_ability="rapid_construction",
            passive_production={
                "construction_speed": 0.2  # +20% build speed na planecie
            },
            description="Construction unit. +20% building construction speed on planet. +15% DEF."
        )


class CyberneticDoctrine(Doctrine):
    """
    Science Level 4 - Cybernetic Enhancement
    Zwiększa efficiency produkcji na planecie
    """
    def __init__(self):
        super().__init__(
            name="Cybernetic",
            strategic_resource="science",
            required_level=4,
            icon="🤖"
        )
        self.cost = {"electronics": 20, "biotech": 10}
        
    def get_effect(self):
        return DoctrineEffect(
            stat_modifiers={
                "attack": 1.20,
                "defense": 1.20,
                "health": 1.30
            },
            special_ability="enhanced_systems",
            passive_production={
                "production_efficiency": 0.05  # +5% all production
            },
            description="Enhanced unit. +20% ATK/DEF, +30% HP. Increases planet production by 5%."
        )


# ============================================
# CULTURE DOCTRINES (influence & conversion)
# ============================================

class DiplomatDoctrine(Doctrine):
    """
    Culture Level 2 - Diplomat
    Może konwertować neutralne planety bez walki
    """
    def __init__(self):
        super().__init__(
            name="Diplomat",
            strategic_resource="culture",
            required_level=2,
            icon="🎭"
        )
        self.cost = {"biotech": 10}
        
    def get_effect(self):
        return DoctrineEffect(
            stat_modifiers={
                "defense": 1.15
            },
            special_ability="peaceful_annexation",
            passive_production={
                "cultural_influence": 1.0
            },
            description="Diplomatic unit. Can convert neutral planets peacefully. Generates 1.0 cultural influence/turn."
        )


class PropagandistDoctrine(Doctrine):
    """
    Culture Level 3 - Propagandist
    Zwiększa happiness i zmniejsza unrest na planecie
    """
    def __init__(self):
        super().__init__(
            name="Propagandist",
            strategic_resource="culture",
            required_level=3,
            icon="📢"
        )
        self.cost = {"biotech": 15, "plastics": 5}
        
    def get_effect(self):
        return DoctrineEffect(
            stat_modifiers={
                "defense": 1.20
            },
            special_ability="morale_boost",
            passive_production={
                "happiness": 0.1,  # +10% happiness
                "unrest_reduction": 0.15  # -15% instability
            },
            description="Morale unit. +10% population happiness, -15% planet instability. +20% DEF."
        )


class CulturalEnvoyDoctrine(Doctrine):
    """
    Culture Level 4 - Cultural Envoy
    Może konwertować wrogie planety przez influence
    """
    def __init__(self):
        super().__init__(
            name="Cultural Envoy",
            strategic_resource="culture",
            required_level=4,
            icon="🌟"
        )
        self.cost = {"biotech": 25, "rare_elements": 5}
        
    def get_effect(self):
        return DoctrineEffect(
            stat_modifiers={
                "defense": 1.30,
                "speed": 1.20
            },
            special_ability="cultural_conquest",
            passive_production={
                "cultural_influence": 2.0
            },
            description="Elite diplomatic unit. Can flip enemy planets through cultural pressure. 2.0 influence/turn."
        )


# ============================================
# FAITH DOCTRINES (morale & population)
# ============================================

class MissionaryDoctrine(Doctrine):
    """
    Faith Level 2 - Missionary
    Nawraca populację, zwiększa wzrost
    """
    def __init__(self):
        super().__init__(
            name="Missionary",
            strategic_resource="faith",
            required_level=2,
            icon="✨"
        )
        self.cost = {"organics": 10}
        
    def get_effect(self):
        return DoctrineEffect(
            stat_modifiers={
                "defense": 1.10
            },
            special_ability="convert_population",
            passive_production={
                "population_growth": 0.15,  # +15% pop growth
                "faith_points": 0.5
            },
            description="Religious unit. +15% population growth on planet. Generates 0.5 faith points/turn."
        )


class TemplarDoctrine(Doctrine):
    """
    Faith Level 3 - Templar
    Zealots - bonus ATK vs non-believers, bonus morale
    """
    def __init__(self):
        super().__init__(
            name="Templar",
            strategic_resource="faith",
            required_level=3,
            icon="⚔️✨"
        )
        self.cost = {"organics": 15, "alloys": 10}
        
    def get_effect(self):
        return DoctrineEffect(
            stat_modifiers={
                "attack": 1.35,
                "defense": 1.20,
                "health": 1.15
            },
            special_ability="holy_fury",
            passive_production={
                "morale": 0.2
            },
            description="Holy warrior. +35% ATK, +20% DEF, +15% HP. Immune to morale penalties. Bonus vs heretics."
        )


class PriestDoctrine(Doctrine):
    """
    Faith Level 4 - High Priest
    Leczy inne jednostki, eliminuje instability
    """
    def __init__(self):
        super().__init__(
            name="High Priest",
            strategic_resource="faith",
            required_level=4,
            icon="🙏"
        )
        self.cost = {"organics": 20, "biotech": 10}
        
    def get_effect(self):
        return DoctrineEffect(
            stat_modifiers={
                "defense": 1.30,
                "health": 1.40
            },
            special_ability="divine_healing",
            passive_production={
                "unit_healing": 0.15,  # +15% healing rate dla wszystkich
                "instability_negation": 1.0  # całkowicie usuwa instability
            },
            description="Spiritual leader. Doubles healing rate for all units. Eliminates planet instability. +30% DEF, +40% HP."
        )


# ============================================
# AUTHORITY DOCTRINES (efficiency & command)
# ============================================

class OfficerDoctrine(Doctrine):
    """
    Authority Level 2 - Officer
    Zwiększa efficiency wszystkich jednostek na planecie
    """
    def __init__(self):
        super().__init__(
            name="Officer",
            strategic_resource="authority",
            required_level=2,
            icon="⚖️"
        )
        self.cost = {"minerals": 10}
        
    def get_effect(self):
        return DoctrineEffect(
            stat_modifiers={
                "attack": 1.15,
                "defense": 1.15
            },
            special_ability="command_bonus",
            passive_production={
                "unit_efficiency": 0.1  # +10% stats dla innych jednostek
            },
            description="Command unit. Grants +10% ATK/DEF to all other units on planet. +15% ATK/DEF."
        )


class CommissarDoctrine(Doctrine):
    """
    Authority Level 3 - Commissar
    Zmniejsza upkeep wszystkich jednostek
    """
    def __init__(self):
        super().__init__(
            name="Commissar",
            strategic_resource="authority",
            required_level=3,
            icon="📋"
        )
        self.cost = {"minerals": 15, "chemicals": 5}
        
    def get_effect(self):
        return DoctrineEffect(
            stat_modifiers={
                "attack": 1.10,
                "defense": 1.25
            },
            special_ability="discipline",
            passive_production={
                "upkeep_reduction": 0.20  # -20% upkeep dla wszystkich
            },
            description="Disciplinarian. Reduces upkeep of all units on planet by 20%. +10% ATK, +25% DEF."
        )


class StrategistDoctrine(Doctrine):
    """
    Authority Level 4 - Strategist
    Umożliwia zaawansowane taktyki i komendy
    """
    def __init__(self):
        super().__init__(
            name="Strategist",
            strategic_resource="authority",
            required_level=4,
            icon="🎖️"
        )
        self.cost = {"minerals": 25, "electronics": 15}
        
    def get_effect(self):
        return DoctrineEffect(
            stat_modifiers={
                "attack": 1.20,
                "defense": 1.30,
                "speed": 1.30
            },
            special_ability="tactical_mastery",
            passive_production={
                "unit_efficiency": 0.20,  # +20% stats dla innych
                "production_speed": 0.15  # +15% military production
            },
            description="Master tactician. +20% stats to all units. +15% military production. +20% ATK, +30% DEF/Speed."
        )


# ============================================
# ARCANE DOCTRINES (special abilities)
# ============================================

class PsionicDoctrine(Doctrine):
    """
    Arcane Level 2 - Psionic
    Teleportacja między planetami
    """
    def __init__(self):
        super().__init__(
            name="Psionic",
            strategic_resource="arcane",
            required_level=2,
            icon="✴️"
        )
        self.cost = {"rare_elements": 15}
        
    def get_effect(self):
        return DoctrineEffect(
            stat_modifiers={
                "attack": 1.25,
                "speed": 2.0  # może się teleportować
            },
            special_ability="teleportation",
            passive_production={
                "arcane_energy": 0.5
            },
            description="Psionic unit. Can teleport between planets instantly. +25% ATK, 2x Speed. Generates arcane energy."
        )


class VoidwalkerDoctrine(Doctrine):
    """
    Arcane Level 3 - Voidwalker
    Przechodzi przez przeszkody, ignoruje terrain
    """
    def __init__(self):
        super().__init__(
            name="Voidwalker",
            strategic_resource="arcane",
            required_level=3,
            icon="🌌"
        )
        self.cost = {"rare_elements": 20, "fuel": 10}
        
    def get_effect(self):
        return DoctrineEffect(
            stat_modifiers={
                "attack": 1.30,
                "defense": 1.20,
                "speed": 1.50
            },
            special_ability="phase_shift",
            passive_production={
                "arcane_energy": 1.0
            },
            description="Reality-bending unit. Ignores terrain, can attack from anywhere. +30% ATK, +20% DEF, +50% Speed."
        )


class RealityWarpDoctrine(Doctrine):
    """
    Arcane Level 4 - Reality Warp
    Może modyfikować produkcję planety losowo
    """
    def __init__(self):
        super().__init__(
            name="Reality Warp",
            strategic_resource="arcane",
            required_level=4,
            icon="🔮"
        )
        self.cost = {"rare_elements": 30, "electronics": 15}
        
    def get_effect(self):
        return DoctrineEffect(
            stat_modifiers={
                "attack": 1.40,
                "defense": 1.40,
                "health": 1.30
            },
            special_ability="chaos_surge",
            passive_production={
                "random_production_bonus": 0.25  # 25% szansa na 2x produkcja
            },
            description="Chaos incarnate. 25% chance to double all production each turn. +40% ATK/DEF, +30% HP."
        )


# ============================================
# DOCTRINE REGISTRY
# ============================================

DOCTRINES = {
    # Military
    "Shock Trooper": ShockTrooperDoctrine,
    "Fortified": FortifiedDoctrine,
    "Elite Guard": EliteGuardDoctrine,
    
    # Science
    "Technician": TechnicianDoctrine,
    "Engineer Corps": EngineerCorpsDoctrine,
    "Cybernetic": CyberneticDoctrine,
    
    # Culture
    "Diplomat": DiplomatDoctrine,
    "Propagandist": PropagandistDoctrine,
    "Cultural Envoy": CulturalEnvoyDoctrine,
    
    # Faith
    "Missionary": MissionaryDoctrine,
    "Templar": TemplarDoctrine,
    "High Priest": PriestDoctrine,
    
    # Authority
    "Officer": OfficerDoctrine,
    "Commissar": CommissarDoctrine,
    "Strategist": StrategistDoctrine,
    
    # Arcane
    "Psionic": PsionicDoctrine,
    "Voidwalker": VoidwalkerDoctrine,
    "Reality Warp": RealityWarpDoctrine,
}


def get_available_doctrines(planet):
    """Zwraca listę doktryn dostępnych na planecie"""
    available = []
    
    for name, doctrine_class in DOCTRINES.items():
        doctrine = doctrine_class()
        if doctrine.can_apply(planet):
            available.append(doctrine)
    
    return available


def apply_doctrine_to_unit(unit, doctrine):
    """Aplikuje doktrynę do jednostki"""
    doctrine.apply_to_unit(unit)
    unit.doctrine_name = doctrine.name
    
    # Jeśli doktryna daje starting XP (Elite Guard)
    if doctrine.name == "Elite Guard":
        unit.experience = 50  # Veteran rank