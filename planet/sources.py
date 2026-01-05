# planet/sources.py
from core.utils import hex_distance

class Source:
    def __init__(self, q, r, strength):
        self.q = q
        self.r = r
        self.strength = strength

    def influence(self, target_hex):
        raise NotImplementedError


class TemperatureSource(Source):
    param = "temperature"
    icon = "temperature"
    def influence(self, h):
        d = hex_distance(self, h)
        radius = 5.0
        if d > radius:
            return 0.0
        falloff = 1.0 - d / radius
        return self.strength * falloff

class ColdSource(Source):
    param = "temperature"
    icon = "cold"
    def influence(self, h):
        d = hex_distance(self, h)
        radius = 5.0
        if d > radius:
            return 0.0
        falloff = 1.0 - d / radius
        return -self.strength * falloff


class HeightSource(Source):
    param = "height"
    icon = "height"

    def influence(self, h):
        d = hex_distance(self, h)
        radius = 5.0
        if d > radius:
            return 0.0
        falloff = 1.0 - d / radius
        falloff = falloff ** 0.6
        return self.strength * falloff


class ErosionSource(Source):
    param = "height"
    icon = "erosion"

    def influence(self, h):
        d = hex_distance(self, h)
        radius = 5.0
        if d > radius:
            return 0.0
        falloff = 1.0 - d / radius
        falloff = falloff ** 0.6
        return -self.strength * falloff

class LifeSource(Source):
    param = "life"
    icon = "life"

    def influence(self, h):
        d = hex_distance(self, h)
        radius = 4.0
        if d > radius:
            return 0.0
        falloff = 1.0 - d / radius
        return self.strength * falloff


class ToxicSource(Source):
    param = "life"
    icon = "toxic"

    def influence(self, h):
        d = hex_distance(self, h)
        radius = 4.0
        if d > radius:
            return 0.0
        falloff = 1.0 - d / radius
        return -self.strength * falloff
