# buildings/Building.py - dodaj metodę build()

class Building:
    def __init__(
        self,
        name,
        category,
        cost=None,
        pop_cost=1.0,
        pop_required=1.0,
        pop_upkeep=0.01,
        energy = 1.0,

        owner=None
    ):
        self.name = name
        self.category = category
        self.cost = cost or {}
        self.pop_cost = pop_cost        
        self.pop_required = pop_required
        self.owner = owner
        self.energy = energy
        self.pop_upkeep = pop_upkeep

    def can_afford(self, planet):
        """Sprawdza czy stać planetę na budowę"""
        if planet.population.size < max(self.pop_required, self.pop_cost):
            return False
        

        for r, v in self.cost.items():
            print(r)
            print(v)
            if planet.storage.get(r, 0) < v:
                return False

        return True

    def pay_cost(self, planet):
        """Płaci koszt budowy"""
        for r, v in self.cost.items():
            planet.storage[r] -= v

        planet.population.size -= self.pop_cost

    def build(self, planet, hex):
        """
        🔨 GŁÓWNA METODA BUDOWY
        Kompletny proces: sprawdzenie -> płatność -> umieszczenie -> efekt
        """
        # 1️⃣ Sprawdzenie czy można zbudować
        if not hex.can_build(self, planet):
            return False, "Cannot build on this hex"
        
        if not self.can_afford(planet):
            return False, f"Cannot afford {self.name}"
        
        # 2️⃣ Płatność
        self.pay_cost(planet)
        
        # 3️⃣ Przypisanie właściciela (jeśli nie ma)
        if not self.owner:
            return False, "Building has no owner"

        # 4️⃣ Umieszczenie na hexie
        hex.add_building(self)
        
        # 5️⃣ Zastosowanie efektu planetarnego
        self.apply_planet_effect(planet)
        
        return True, f"{self.name} built successfully"

    def produce(self, hex, population):
        return {}
    
    def blocks_hex(self):
        return False

    def apply_planet_effect(self, planet):
        """Efekt budynku na planetę (override w podklasach)"""
        pass

    def limit_key(self):
        return None