class Building:
    def __init__(
        self,
        name,
        category,
        cost=None,
        pop_cost=0.0,
        pop_required=0.0,
        pop_upkeep=0.0,
        owner=None
    ):
        self.name = name
        self.category = category
        self.cost = cost or {}

        self.pop_cost = pop_cost        
        self.pop_required = pop_required
        self.owner=owner
        self.pop_upkeep = pop_upkeep    # ciągłe

    def can_afford(self, planet):
        if planet.population.size < self.pop_required:
            
            return False
        if  planet.population.can_support(self.pop_upkeep):
            return False

        for r, v in self.cost.items():
            if planet.storage.get(r, 0) < v:
                return False

        return True

    def pay_cost(self, planet):
        for r, v in self.cost.items():
            planet.storage[r] -= v

        planet.population.size -= self.pop_cost
        planet.population.add_load(self.pop_upkeep)

    def produce(self, hex, population):
        return {}
    
    def blocks_hex(self):
        return False

    def apply_planet_effect(self, planet):
        pass

    def limit_key(self):
        return None 