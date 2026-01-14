# empire/empire.py - UPDATED
import logging
from ai.simple_ai import SimpleAI
from empire.transport import TransportManager
from military.units import EmpireMilitaryManager

class Empire:
    def __init__(self, name, color, galaxy, is_player=False, cash=200):
        self.name = name
        self.color = color
        self.galaxy = galaxy
        self.cash = cash
        self.is_player = is_player
        self.cash_last = 100.0
        self.planets = []
        
        # ✅ NOWY: Transport + Military managers
        self.transport_manager = TransportManager(self)
        self.military_manager = EmpireMilitaryManager(self)

        # If `planets` was pre-filled, ensure ownership is consistent
        for p in list(self.planets):
            try:
                p.set_owner(self)
                p.colonized = True
            except Exception:
                pass

        self.ai = None
        if not is_player:
            self.ai = SimpleAI(self, galaxy)

    def tick(self):
        # ✅ NOWY: Tick transportów
        self.military_manager.tick()
        self.transport_manager.tick()
        
        if not self.is_player:
            self.ai.tick()
        # Usuń martwe kolonie (populacja 0) by nie pojawiały się w statusie
        for p in list(self.planets):
            try:
                if getattr(p, 'colonized', False) and getattr(p, 'population', None) and p.population.size <= 0.0:
                    p.set_owner(None)
            except Exception:
                pass

        for p in list(self.planets):
            if p.owner is not self:
                logging.warning("PLANET OWNER DESYNC %s", p)
        
    def status(self, galaxy):
        logging.info("=== %s STATUS ===", self.name)
        
        # Pokaż aktywne transporty
        if self.transport_manager.transports:
            logging.info("Active transports: %d", len(self.transport_manager.transports))
            for t in self.transport_manager.transports:
                source_sys, source_orbit = t.source.get_location(galaxy)
                target_sys, target_orbit = t.target.get_location(galaxy)
        
        for p in self.planets:
            system, orbit = p.get_location(galaxy)
            pos = f"System {system.star.type if system else '??'}, Orbit {orbit}" 
            logging.info("Planet %s @ %s: Population=%.1f, Buildings=%s", id(p), pos, p.population.size, p.buildings_summary())

    def add_planet(self, planet):
        if planet not in self.planets:
            try:
                planet.set_owner(self)
            except Exception:
                planet.owner = self
            
    def can_colonize(self, planet):
        return not planet.colonized
        
    def create_transport(self, source, target, cargo, transport_type="resources"):
        """Wrapper dla tworzenia transportu"""
        return self.transport_manager.create_transport(source, target, cargo, transport_type)
    
    def sell_resources(self, planet, resource, amount, price_per_unit):
        """Sell `amount` of `resource` from `planet` for `price_per_unit` each.

        Returns revenue (0.0 if insufficient stock).
        """
        try:
            if planet.storage.get(resource, 0.0) < amount:
                logging.debug("Not enough %s to sell from planet %s", resource, id(planet))
                return 0.0

            planet.storage[resource] -= amount
            revenue = amount * price_per_unit
            self.cash += revenue
            logging.info("%s sold %.1f %s from planet %s for %.2f cash", self.name, amount, resource, id(planet), revenue)
            return revenue
        except Exception:
            # safe fallback: do nothing on unexpected errors
            return 0.0