from buildings.Building import Building
from core.config import BUILDING_MAJOR, BASIC_RESOURCES
from planet.resources import RESOURCE_EXTREMES

REFINERY_EFFICIENCY = 0.5

from core.config import BASIC_RESOURCES
from core.config import ENVIRONMENT_WEIGHTS


class Refinery(Building):
    BASE_THROUGHPUT = 2.0
    BASE_EFFICIENCY = 0.5
    workers_required = 0.8
    energy_cost = 0.6

    def __init__(self, resource_in, resource_out):
        name = f"{resource_in.capitalize()} Refinery"
        super().__init__(name, BUILDING_MAJOR, cost={resource_in: 5})
        self.resource_in = resource_in
        self.resource_out = resource_out
        self.mode_cooldown = 0  # tick po zmianie trybu

    # =========================
    # TRYB PRACY
    # =========================
    def set_mode(self, resource):
        if resource not in BASIC_RESOURCES:
            return False

        self.input_resource = resource
        self.cost = {resource: 5}
        self.mode_cooldown = 1
        return True

    # =========================
    # PRODUKCJA
    # =========================
    def produce(self, hex, population):
        planet = hex.planet

        base_input = 1.0
        base_output = 0.6

        # 1️⃣ ekstremum właściwe dla surowca
        stat = RESOURCE_EXTREMES.get(self.resource_in)
        extreme = planet.extreme_level(stat) if stat else 0.0

        # 2️⃣ globalna niestabilność planety
        instability = planet.instability()

        # 3️⃣ populacja reaguje SILNIEJ niż w kopalniach
        pop_bonus = population.bonus(self.resource_in)

        # 4️⃣ koszt wejściowy rośnie gwałtownie
        input_mult = 1.0 + extreme * 1.5 + instability * 0.8

        # 5️⃣ output lekko maleje
        output_mult = max(0.3, 1.0 - extreme * 0.6)

        # 6️⃣ realne wartości
        input_amount = base_input * input_mult
        output_amount = base_output * output_mult * pop_bonus

        # 7️⃣ brak surowców → brak produkcji
        if planet.storage.get(self.resource_in, 0.0) < input_amount:
            return {}

        planet.storage[self.resource_in] -= input_amount

        return {
            self.resource_out: output_amount
        }

    # =========================
    # ENVIRONMENT
    # =========================
    def environment_factor(self, hex, planet):
        weights = ENVIRONMENT_WEIGHTS.get(self.output_resource, {})
        factor = 1.0

        for attr, weight in weights.items():
            val = getattr(hex, attr)
            factor += val * weight

        return max(0.3, min(1.5, factor))

    # =========================
    # UI
    # =========================
    def description(self):
        if self.input_resource:
            return f"{self.input_resource} → {self.output_resource}"
        return "No mode selected"
