"""
military/population_synergy.py
System łączący statystyki populacji z jednostkami wojskowymi
"""

# ============================================
# MAPOWANIE STATÓW POPULACJI NA JEDNOSTKI
# ============================================

POPULATION_STAT_BONUSES = {
    # Podstawowe zasoby → statystyki jednostek
    "energy": {
        "attack": 0.015,      # +1.5% ATK za każdy punkt energy stat
        "speed": 0.01,        # +1% Speed
        "upkeep": 0.008       # ✅ +0.8% upkeep (specialized = expensive)
    },
    "minerals": {
        "defense": 0.02,      # +2% DEF za każdy punkt minerals stat
        "health": 0.015,      # +1.5% HP
        "upkeep": 0.012       # ✅ +1.2% upkeep (heavy armor = expensive)
    },
    "organics": {
        "health": 0.025,      # +2.5% HP za każdy punkt organics stat
        "upkeep": -0.005      # -0.5% upkeep (bio-efficient = cheaper!)
    },
    "water": {
        "health": 0.01,       # +1% HP
        "upkeep": -0.003      # -0.3% upkeep (water = sustenance)
    },
    "gases": {
        "speed": 0.02,        # +2% Speed za każdy punkt gases stat
        "attack": 0.01,       # +1% ATK
        "upkeep": 0.006       # ✅ +0.6% upkeep (exotic propulsion = expensive)
    },
    "rare_elements": {
        "attack": 0.02,       # +2% ATK za każdy punkt rare_elements
        "defense": 0.02,      # +2% DEF
        "health": 0.01,       # +1% HP
        "upkeep": 0.015       # ✅ +1.5% upkeep (elite tech = very expensive!)
    }
}


# ============================================
# OBLICZANIE BONUSÓW Z POPULACJI
# ============================================

def calculate_population_bonuses(planet):
    """
    Oblicza modyfikatory jednostek na podstawie statów populacji
    
    Returns:
        dict: {"attack": 1.25, "defense": 1.30, "health": 1.20, "speed": 1.15, "upkeep": 1.10}
    """
    if not planet.colonized or not planet.population:
        return {
            "attack": 1.0,
            "defense": 1.0,
            "health": 1.0,
            "morale": 1.0,
            "speed": 1.0,
            "upkeep": 1.0
        }
    
    pop_stats = planet.population.stats
    modifiers = {
        "attack": 1.0,
        "defense": 1.0,
        "health": 1.0,
        "speed": 1.0,
        "morale": 1.0,
        "upkeep": 1.0
    }
    
    # Dla każdego statu populacji
    for resource, stat_value in pop_stats.items():
        if resource not in POPULATION_STAT_BONUSES:
            continue
        
        bonus_mapping = POPULATION_STAT_BONUSES[resource]
        
        # Aplikuj bonusy
        for unit_stat, bonus_per_point in bonus_mapping.items():
            # stat_value może być 0-10 (typowo)
            # bonus = stat_value * bonus_per_point
            # np. 8.0 minerals * 0.02 = 0.16 = +16% defense
            modifier_change = stat_value * bonus_per_point
            modifiers[unit_stat] += modifier_change
    
    # Upkeep nie może spaść poniżej 0.5x (max 50% redukcja)
    modifiers["upkeep"] = max(0.5, modifiers["upkeep"])
    
    # Inne staty max 2.5x (cap at +150%)
    for stat in ["attack", "defense", "health", "speed"]:
        modifiers[stat] = min(2.5, modifiers[stat])
    
    return modifiers


def apply_population_bonuses_to_unit(unit, planet):
    """
    Aplikuje bonusy z populacji do jednostki podczas produkcji
    """
    bonuses = calculate_population_bonuses(planet)
    
    # Aplikuj do statystyk
    unit.stats.attack *= bonuses["attack"]
    unit.stats.defense *= bonuses["defense"]
    unit.stats.health *= bonuses["health"]
    unit.stats.morale *= bonuses["morale"]
    unit.stats.speed *= int(bonuses["speed"])  # Speed to int
    unit.stats.upkeep *= bonuses["upkeep"]
    
    # Zapisz bonusy do jednostki (dla UI)
    unit.population_bonuses = bonuses
    unit.birth_planet = planet
    
    # Aktualizuj current_health do nowego max
    unit.current_health = unit.stats.health


# ============================================
# WYŚWIETLANIE BONUSÓW
# ============================================

def get_population_bonus_summary(planet):
    """
    Zwraca czytelne podsumowanie bonusów dla UI
    
    Returns:
        list: ["ATK: +25%", "DEF: +30%", "HP: +20%", "Upkeep: +10%"]
    """
    bonuses = calculate_population_bonuses(planet)
    
    summary = []
    
    for stat, multiplier in bonuses.items():
        if stat == "speed" and multiplier == 1.0:
            continue  # Skip speed if no bonus
            
        percent = int((multiplier - 1.0) * 100)
        
        if percent == 0:
            continue
        
        stat_display = {
            "attack": "ATK",
            "defense": "DEF",
            "health": "HP",
            "morale": "morale",
            "speed": "SPD",
            "upkeep": "Upkeep"
        }[stat]
        
        summary.append(f"{stat_display}: {percent:+d}%")
    
    return summary


def get_detailed_bonus_breakdown(planet):
    """
    Szczegółowy breakdown dla tooltipa
    
    Returns:
        dict: {
            "energy": {"attack": +12%, "speed": +8%},
            "minerals": {"defense": +16%, "health": +12%},
            ...
        }
    """
    if not planet.colonized or not planet.population:
        return {}
    
    pop_stats = planet.population.stats
    breakdown = {}
    
    for resource, stat_value in pop_stats.items():
        if resource not in POPULATION_STAT_BONUSES:
            continue
        
        if stat_value < 0.1:  # Skip negligible stats
            continue
        
        bonus_mapping = POPULATION_STAT_BONUSES[resource]
        resource_bonuses = {}
        
        for unit_stat, bonus_per_point in bonus_mapping.items():
            bonus_percent = int(stat_value * bonus_per_point * 100)
            
            if bonus_percent != 0:
                resource_bonuses[unit_stat] = bonus_percent
        
        if resource_bonuses:
            breakdown[resource] = resource_bonuses
    
    return breakdown


# ============================================
# PRZYKŁADY UŻYCIA
# ============================================

def example_planet_bonuses():
    """
    Przykładowe scenariusze bonusów
    """
    
    # Planeta górnicza (high minerals, energy)
    mining_planet_stats = {
        "energy": 8.0,
        "minerals": 10.0,
        "organics": 2.0,
        "water": 3.0,
        "gases": 1.0,
        "rare_elements": 0.5
    }
    
    # Bonusy:
    # energy: +12% ATK, +8% Speed
    # minerals: +20% DEF, +15% HP
    # organics: +5% HP, -1% upkeep
    # water: +3% HP, -0.9% upkeep
    # Total: ATK +12%, DEF +20%, HP +23%, Speed +8%, Upkeep -1.9%
    
    # Planeta rolnicza (high organics, water)
    farming_planet_stats = {
        "energy": 2.0,
        "minerals": 3.0,
        "organics": 10.0,
        "water": 9.0,
        "gases": 1.0,
        "rare_elements": 0.5
    }
    
    # Bonusy:
    # energy: +3% ATK, +2% Speed
    # minerals: +6% DEF, +4.5% HP
    # organics: +25% HP, -5% upkeep (!!!)
    # water: +9% HP, -2.7% upkeep
    # Total: ATK +3%, DEF +6%, HP +38.5%, Upkeep -7.7%
    # = Tanky, cheap units
    
    # Planeta technologiczna (high rare_elements, gases)
    tech_planet_stats = {
        "energy": 5.0,
        "minerals": 4.0,
        "organics": 3.0,
        "water": 2.0,
        "gases": 8.0,
        "rare_elements": 7.0
    }
    
    # Bonusy:
    # energy: +7.5% ATK, +5% Speed
    # minerals: +8% DEF, +6% HP
    # organics: +7.5% HP, -1.5% upkeep
    # water: +2% HP, -0.6% upkeep
    # gases: +16% Speed, +8% ATK
    # rare_elements: +14% ATK, +14% DEF, +7% HP, +7% upkeep
    # Total: ATK +29.5%, DEF +22%, HP +22.5%, Speed +21%, Upkeep +4.9%
    # = Elite glass cannons, expensive


# ============================================
# INTEGRATION HELPERS
# ============================================

def format_unit_stats_with_bonuses(unit, base_unit):
    """
    Formatuje statystyki jednostki pokazując bazę i bonusy
    
    Args:
        unit: Wyprodukowana jednostka (z bonusami)
        base_unit: Czysta jednostka bazowa (bez bonusów)
    
    Returns:
        dict: {
            "attack": {"base": 10, "current": 13, "bonus": "+30%"},
            "defense": {"base": 8, "current": 10, "bonus": "+25%"},
            ...
        }
    """
    result = {}
    
    for stat in ["attack", "defense", "health", "speed", "upkeep"]:
        base_value = getattr(base_unit.stats, stat)
        current_value = getattr(unit.stats, stat)
        
        if base_value == 0:
            continue
        
        bonus_percent = int(((current_value / base_value) - 1.0) * 100)
        
        result[stat] = {
            "base": base_value,
            "current": current_value,
            "bonus": f"{bonus_percent:+d}%"
        }
    
    return result


def get_recruitment_preview(planet, unit_class):
    """
    Pokazuje preview jednostki PRZED rekrutacją
    
    Returns:
        dict: Statystyki jakie będzie miała jednostka
    """
    # Stwórz testową jednostkę
    preview_unit = unit_class()
    base_unit = unit_class()
    
    # Aplikuj bonusy
    apply_population_bonuses_to_unit(preview_unit, planet)
    
    return {
        "base_stats": {
            "attack": base_unit.stats.attack,
            "defense": base_unit.stats.defense,
            "health": base_unit.stats.health,
            "speed": base_unit.stats.speed,
            "upkeep": base_unit.stats.upkeep
        },
        "actual_stats": {
            "attack": preview_unit.stats.attack,
            "defense": preview_unit.stats.defense,
            "health": preview_unit.stats.health,
            "speed": preview_unit.stats.speed,
            "upkeep": preview_unit.stats.upkeep
        },
        "bonuses": preview_unit.population_bonuses
    }