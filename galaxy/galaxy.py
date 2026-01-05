# galaxy/galaxy.py
from core.rng import uniform
from galaxy.system import StarSystem
import math
import random
from empire.empire import Empire
class Galaxy:
    def __init__(self, system_count=20, size=1000, links_per_system=3):
        self.systems = []
        self.empires = []
        self.turn = 0

        self.generate(system_count, size)
        self._generate_links(links_per_system)
        self._connect_components()


    def _generate_links(self, n):
        for s in self.systems:
            distances = []

            for other in self.systems:
                if other is s:
                    continue
                dx = s["x"] - other["x"]
                dy = s["y"] - other["y"]
                d = math.sqrt(dx * dx + dy * dy)
                distances.append((d, other))

            distances.sort(key=lambda x: x[0])

            for _, target in distances[:n]:
                if target not in s["links"]:
                    s["links"].append(target)
                if s not in target["links"]:
                    target["links"].append(s)
  
    def _find_components(self):
        visited = set()
        components = []

        for s in self.systems:
            if s["id"] in visited:
                continue

            stack = [s]
            group = []

            while stack:
                current = stack.pop()
                cid = current["id"]

                if cid in visited:
                    continue

                visited.add(cid)
                group.append(current)

                for n in current["links"]:
                    if n["id"] not in visited:
                        stack.append(n)

            components.append(group)

        return components


    def _connect_components(self):
        components = self._find_components()

        while len(components) > 1:
            a = components[0]
            b = components[1]
            best_pair = None
            best_dist = float("inf")

            for s1 in a:
                for s2 in b:
                    dx = s1["x"] - s2["x"]
                    dy = s1["y"] - s2["y"]
                    d = dx * dx + dy * dy
                    if d < best_dist:
                        best_dist = d
                        best_pair = (s1, s2)

            s1, s2 = best_pair
            s1["links"].append(s2)
            s2["links"].append(s1)

            components = self._find_components()


    def produce(self):
        total = {}

        for entry in self.systems:
            system = entry["system"]
            prod = system.produce()

            for res, val in prod.items():
                total[res] = total.get(res, 0.0) + val

        return total

    def tick(self):
        self.turn += 1
        # 1️⃣ AI imperiów
        for empire in self.empires:
            empire.tick()
            empire.status(self)
            energy_delta = 0.0

            for planet in empire.planets:
                energy_delta += planet.energy_delta()  # ✅ NAWIASY

            empire.storage["energy"] += energy_delta
            empire.energy_last = energy_delta

            if empire.storage["energy"] < 0:
                self.energy_crisis(empire)
                
        # 2️⃣ Tick planet
        for entry in self.systems:
            system = entry["system"]
            for planet in system.planets:
                planet.tick()



    def generate(self, system_count, size):
        for i in range(system_count):
            x = random.randint(50, size - 50)
            y = random.randint(50, size - 50)

            system = StarSystem()

            node = {
                "id": i,
                "x": x,
                "y": y,
                "system": system,
                "links": []
            }

            self.systems.append(node)
            
            
            
    def energy_crisis(self, empire):
        empire.storage["energy"] = 0

        for planet in empire.planets:
            planet.population.size *= 0.98  
