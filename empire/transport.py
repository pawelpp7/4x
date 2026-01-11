"""
empire/transport.py
System transportu zasobów i populacji między planetami
"""

class Transport:
    """Pojedynczy transport w drodze"""
    
    def __init__(self, source_planet, target_planet, cargo, transport_type="resources"):
        self.source = source_planet
        self.target = target_planet
        self.cargo = cargo  # dict dla zasobów lub float dla populacji
        self.transport_type = transport_type  # "resources" lub "population"
        
        # Oblicz czas transportu na podstawie odległości
        self.time_total = self._calculate_travel_time()
        self.time_remaining = self.time_total
        self.status = "in_transit"  # in_transit, delivered, cancelled
        
    def _calculate_travel_time(self):
        """Oblicza czas podróży na podstawie odległości systemów"""
        # Zakładamy że oba planety mają dostęp do galaxy przez source
        if not hasattr(self.source, 'owner'):
            return 5
            
        empire = self.source.owner
        if not hasattr(empire, 'galaxy'):
            return 5
            
        galaxy = empire.galaxy
        
        # Znajdź systemy
        source_system = None
        target_system = None
        
        for entry in galaxy.systems:
            if self.source in entry["system"].planets:
                source_system = entry
            if self.target in entry["system"].planets:
                target_system = entry
                
        if not source_system or not target_system:
            return 5
            
        # Ten sam system = 3 tury
        if source_system == target_system:
            return 3
            
        # Sąsiednie systemy = 5 tur
        if target_system in source_system["links"]:
            return 5
            
        # Dalsze systemy = 8+ tur (można rozbudować o pathfinding)
        return 8
        
    def tick(self):
        """Aktualizacja transportu co turę"""
        if self.status != "in_transit":
            return False
            
        self.time_remaining -= 1
        
        if self.time_remaining <= 0:
            self._deliver()
            return True
            
        return False
        
    def _deliver(self):
        """Dostarcza ładunek do celu"""
        if self.transport_type == "resources":
            for res, amount in self.cargo.items():
                self.target.storage[res] = self.target.storage.get(res, 0) + amount
        elif self.transport_type == "population":
            pop_amount = self.cargo
            self.target.population.size += pop_amount
            
        self.status = "delivered"
        
    def progress(self):
        """Zwraca procent ukończenia podróży"""
        return 1.0 - (self.time_remaining / self.time_total)
        
    def cancel(self):
        """Anuluje transport - zasoby wracają do źródła"""
        if self.status != "in_transit":
            return False
            
        if self.transport_type == "resources":
            for res, amount in self.cargo.items():
                self.source.storage[res] = self.source.storage.get(res, 0) + amount
        elif self.transport_type == "population":
            self.source.population.size += self.cargo
            
        self.status = "cancelled"
        return True


class TransportManager:
    """Zarządza wszystkimi transportami w imperium"""
    
    def __init__(self, empire):
        self.empire = empire
        self.transports = []  # lista aktywnych transportów
        self.history = []     # ostatnie 10 dostaw (dla UI)
        
    def create_transport(self, source, target, cargo, transport_type="resources"):
        """Tworzy nowy transport"""
        
        # Walidacja
        if source.owner != self.empire or target.owner != self.empire:
            return False, "Both planets must belong to your empire"
            
        if not source.colonized or not target.colonized:
            return False, "Both planets must be colonized"
            
        # Sprawdź dostępność zasobów/populacji
        if transport_type == "resources":
            for res, amount in cargo.items():
                if source.storage.get(res, 0) < amount:
                    return False, f"Not enough {res} on source planet"
            
            # Odejmij zasoby ze źródła
            for res, amount in cargo.items():
                source.storage[res] -= amount
                
        elif transport_type == "population":
            pop_amount = cargo
            if source.population.size < pop_amount:
                return False, "Not enough population on source planet"
            
            # Odejmij populację ze źródła
            source.population.size -= pop_amount
            
        # Utwórz transport
        transport = Transport(source, target, cargo, transport_type)
        self.transports.append(transport)
        
        return True, f"Transport created: {transport.time_total} turns"
        
    def tick(self):
        """Aktualizuje wszystkie transporty"""
        completed = []
        
        for transport in self.transports:
            if transport.tick():  # zwraca True gdy dostarczono
                completed.append(transport)
                self._add_to_history(transport)
                
        # Usuń zakończone transporty
        for t in completed:
            self.transports.remove(t)
            
    def _add_to_history(self, transport):
        """Dodaje transport do historii"""
        self.history.append({
            "source": transport.source,
            "target": transport.target,
            "cargo": transport.cargo,
            "type": transport.transport_type,
            "status": transport.status
        })
        
        # Ogranicz historię do 10 ostatnich
        if len(self.history) > 10:
            self.history.pop(0)
            
    def get_active_transports_for_planet(self, planet):
        """Zwraca transporty związane z daną planetą"""
        return [
            t for t in self.transports 
            if t.source == planet or t.target == planet
        ]


# ============================================
# POMOCNICZE FUNKCJE
# ============================================

def can_transport_between(source, target, galaxy):
    """Sprawdza czy możliwy jest transport między planetami"""
    if source == target:
        return False, "Cannot transport to same planet"
        
    if source.owner != target.owner:
        return False, "Planets must have same owner"
        
    if not source.colonized or not target.colonized:
        return False, "Both planets must be colonized"
        
    # Sprawdź czy planety są połączone (opcjonalne - można wymagać połączenia)
    # Na razie zakładamy że każda planeta może wysłać do każdej w imperium
    
    return True, "OK"


def calculate_transport_cost(source, target, cargo, galaxy):
    """
    Oblicza koszt energii transportu
    Można rozbudować o koszty w zależności od odległości
    """
    source_system = None
    target_system = None
    
    for entry in galaxy.systems:
        if source in entry["system"].planets:
            source_system = entry
        if target in entry["system"].planets:
            target_system = entry
            
    if not source_system or not target_system:
        return 0
        
    # Ten sam system = 5 energii
    if source_system == target_system:
        return 5
        
    # Sąsiednie systemy = 10 energii
    if target_system in source_system["links"]:
        return 10
        
    # Dalsze systemy = 20 energii
    return 20