# planet/hex_map.py
from planet.hex import Hex

class HexMap:
    def __init__(self, radius):
        self.hexes = []

        for q in range(-radius, radius + 1):
            for r in range(-radius, radius + 1):
                if abs(q + r) <= radius:
                    self.hexes.append(Hex(q, r))

    def apply_temperature_gradient(self, base_temp):
        for hex in self.hexes:
            dist = abs(hex.q) + abs(hex.r)
            hex.temperature = base_temp - dist * 0.15
