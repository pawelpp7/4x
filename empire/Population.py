POP_STATS = [
    "thermal",
    "cryo",
    "fluidics",
    "solids",
    "biomass",
    "exotics",
]

class Population:
    def __init__(self, size=7.0):
        self.size = size
        self.used = 0.0
        self.growth=0.01
        self.happiness=1.0

        self.stats = {
            "thermal": 0.0,
            "cryo": 0.0,
            "fluidics": 0.0,
            "solids": 0.0,
            "biomass": 0.0,
            "exotics": 0.0,
        }

    @property
    def free(self):
        return max(0.0, self.size - self.used)

    def bonus(self, resource):
        return 1.0 + self.stats.get(resource, 0.0) * 0.05

    def can_support(self, load):
        return self.used + load <= self.size

    def add_load(self, load):
        self.used += load
