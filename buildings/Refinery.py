from buildings.Building import Building
from core.config import BUILDING_MAJOR, BASIC_RESOURCES
from empire.buffs import population_resource_bonus
from planet.resources import RESOURCE_EXTREMES

REFINERY_EFFICIENCY = 0.5

from core.config import BASIC_RESOURCES
from core.config import ENVIRONMENT_WEIGHTS

class Refinery(Building):
    workers_required = 0.08
    cash_cost = 0.6
    pop_upkeep=0.1,

    def __init__(self, name, inputs, output, extreme_bonus_type=None):
        """
        inputs: dict[str, float]
        output: (resource: str, amount: float)
        extreme_bonus_type: str | None
        """
        super().__init__(name, BUILDING_MAJOR, cost=inputs)

        self.inputs = inputs
        self.operational_cost = inputs
        self.output_resource, self.base_output = output
        self.extreme_bonus_type = extreme_bonus_type

    # =========================
    # PRODUKCJA
    # =========================
    def produce(self, hex, population):
        delta = {}

        total_work_bonus = 1.0

        # 1️⃣ INPUTY – każdy z bonusem populacji
        for res, base_amount in self.inputs.items():
            pop_bonus = population_resource_bonus(population, res)

            # populacja = wydajniejsza, ALE też więcej zużywa
            input_amount = base_amount * pop_bonus

            delta[res] = -input_amount

            # wkład pracy do outputu
            total_work_bonus *= pop_bonus

        # 2️⃣ BONUS OD EKSTREMUM HEXA
        if self.extreme_bonus_type:
            extreme = getattr(hex, self.extreme_bonus_type, 0.0)
            total_work_bonus *= (1.0 + extreme * 0.5)

        # 3️⃣ OUTPUT
        output_amount = self.base_output * total_work_bonus
        delta[self.output_resource] = output_amount

        return delta



    # =========================
    # ENVIRONMENT
    # =========================
    def environment_factor(self, hex, planet):
        weights = ENVIRONMENT_WEIGHTS.get(self.output_resource, {})
        factor = 1.0

        for attr, weight in weights.items():
            factor += getattr(hex, attr, 0.0) * weight

        return max(0.3, min(1.5, factor))

    # =========================
    # UI
    # =========================
    def description(self):
        ins = ", ".join(f"{k}:{v}" for k, v in self.inputs.items())
        return f"{ins} → {self.output_resource}"

class Smelter(Refinery):
    """
    Przetapia minerały w stopy metali
    Bonus: extreme temperature (wysoka temp = lepsze topienie)
    """
    def __init__(self):
        super().__init__(
            name="Smelter",
            inputs={"minerals": 2.0, "energy": 1.0},
            output=("alloys", 1.5),
            extreme_bonus_type="temperature"
        )


# ============================================
# CHEMICAL PLANT - Zakład chemiczny
# ============================================
class ChemicalPlant(Refinery):
    """
    Przetwarza gazy i wodę w chemikalia
    Bonus: extreme height (wysokie ciśnienie = lepsze reakcje)
    """
    def __init__(self):
        super().__init__(
            name="Chemical Plant",
            inputs={"gases": 1.5, "water": 1.0, "energy": 0.5},
            output=("chemicals", 2.0),
            extreme_bonus_type="height"
        )


# ============================================
# BIOREACTOR - Bioreaktor
# ============================================
class Bioreactor(Refinery):
    """
    Przetwarza organikę w biotechnologię
    Bonus: extreme life (różnorodne życie = lepsze biotech)
    """
    def __init__(self):
        super().__init__(
            name="Bioreactor",
            inputs={"organics": 2.0, "water": 1.0},
            output=("biotech", 1.2),
            extreme_bonus_type="life"
        )


# ============================================
# POLYMER FACTORY - Fabryka tworzyw
# ============================================
class PolymerFactory(Refinery):
    """
    Polimeryzuje organikę i chemikalia w tworzywa
    Bonus: erosion (chaos procesów = ciekawsze polimery)
    """
    def __init__(self):
        super().__init__(
            name="Polymer Factory",
            inputs={"organics": 1.5, "chemicals": 1.0},
            output=("plastics", 2.0),
            extreme_bonus_type="erosion"  # erosion = chaos
        )


# ============================================
# ELECTRONICS FAB - Fabryka elektroniki
# ============================================
class ElectronicsFab(Refinery):
    """
    Wytwarza elektronikę z minerałów i rzadkich elementów
    Bonus: cold (stabilne, niskie temperatury dla półprzewodników)
    """
    def __init__(self):
        super().__init__(
            name="Electronics Fab",
            inputs={"minerals": 1.0, "rare_elements": 0.5, "energy": 0.5},
            output=("electronics", 0.8),
            extreme_bonus_type="cold"  # cold = stable temps
        )
    
    def calculate_bonus(self, planet, population):
        """
        Override: Electronics potrzebuje STABILNYCH warunków
        Wysoka temperatura/toxic = KARA (clean room needed)
        Niskie temp (cold) = BONUS
        """
        bonus = 1.0
        
        # Bonus za zimno (stabilność)
        cold_extreme = planet.extreme_level("cold") if hasattr(planet, 'extreme_level') else 0
        cold_bonus = 1.0 + cold_extreme * 0.6
        bonus *= cold_bonus
        
        # KARA za toxic (brudne środowisko)
        toxic_sources = [s for s in planet.sources if getattr(s, 'icon', '') == 'toxic']
        if toxic_sources:
            toxic_penalty = 0.7  # -30% output
            bonus *= toxic_penalty
        
        # Populacja
        pop_bonus = population.bonus("minerals")
        bonus *= pop_bonus
        
        return bonus


# ============================================
# FUEL REFINERY - Rafineria paliw
# ============================================
class FuelRefinery(Refinery):
    """
    Rafinuje paliwa z organiki, chemikaliów i gazów
    Bonus: toxic (trudne warunki = lepsze synteza wysokoenergetyczna)
    """
    def __init__(self):
        super().__init__(
            name="Fuel Refinery",
            inputs={"organics": 1.0, "chemicals": 0.5, "gases": 0.5},
            output=("fuel", 1.5),
            extreme_bonus_type="toxic"
        )


# ============================================
# Export all
# ============================================
__all__ = [
    'Smelter',
    'ChemicalPlant',
    'Bioreactor',
    'PolymerFactory',
    'ElectronicsFab',
    'FuelRefinery',
]