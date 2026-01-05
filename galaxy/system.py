# galaxy/system.py
from core.rng import randint
from galaxy.star import Star
from planet.planet import Planet


class StarSystem:
    def __init__(self):
        # ⭐ gwiazda
        self.star = Star()

        # 🪐 planety
        self.planets = []

        count = randint(*self.star.planet_range)

        for _ in range(count):
            planet = Planet()
            planet.base_temperature = self.star.temp_bias
            self.planets.append(planet)

    def summary(self):
        return {
            "star": self.star.type,
            "planets": len(self.planets)
        }

    def produce(self):
        total = {}

        for p in self.planets:
            prod = p.produce()
            for res, val in prod.items():
                total[res] = total.get(res, 0.0) + val

        return total
