"""
military/combat.py - UPDATED VERSION
Dodaj tę klasę do istniejącego pliku military/combat.py
"""


from military.combat import CombatResolver


class PlanetaryInvasion:
    """System desantu na planetę"""
    
    def __init__(self, attacking_empire, target_planet, invasion_force):
        self.attacker = attacking_empire
        self.target = target_planet
        self.invasion_force = invasion_force
        self.status = "in_progress"
        self.combat_log = ["=== INVASION STARTED ==="]
        
        # Resolver walki
        self.resolver = None
        
    def tick(self):
        """Postęp inwazji co turę"""
        if self.status != "in_progress":
            return
        
        garrison = self.target.military_manager.garrison
        
        # Brak obrońców = instant win
        if not garrison:
            self._capture_planet()
            return
        
        # Stwórz resolver jeśli nie ma
        if not self.resolver:
            self.resolver = CombatResolver(
                self.invasion_force,
                garrison,
                location=self.target
            )
            self.combat_log = self.resolver.log
        
        # Tick walki
        self.resolver.tick()
        self.combat_log = self.resolver.log
        
        # Sprawdź koniec
        if self.resolver.finished:
            if self.resolver.winner == "attacker":
                self._capture_planet()
            else:
                self.status = "failed"
                self.combat_log.append(f"[INVASION] {self.attacker.name} invasion FAILED!")
            
            # Usuń zniszczone jednostki
            self.invasion_force = [u for u in self.invasion_force if u.current_health > 0]
            self.target.military_manager.garrison = [u for u in garrison if u.current_health > 0]
    
    def _capture_planet(self):
        if self.status == "successful":
            return

        self.target.set_owner(self.attacker)

        self.target.colonized = True
        self.target.colonization_state = "colonized"

        self.target.military_manager.garrison = list(self.invasion_force)

        self.status = "successful"

        msg = f"[INVASION] {self.attacker.name} captured planet!"
        print(msg)
        self.combat_log.append(msg)
