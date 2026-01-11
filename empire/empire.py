# empire/empire.py - UPDATED
from ai.simple_ai import SimpleAI
from empire.transport import TransportManager
from military.units import EmpireMilitaryManager

class Empire:
    def __init__(self, name, color, galaxy, is_player=False, energy=200):
        self.name = name
        self.color = color
        self.galaxy = galaxy
        self.energy = energy
        self.is_player = is_player
        self.energy_last = 100.0
        self.planets = []
        
        # ✅ NOWY: Transport Manager
        self.transport_manager = TransportManager(self)
        
        for p in self.planets:
            p.owner = self
            p.colonized = True
            self.planets.append(p)
        self.military_manager = EmpireMilitaryManager(self)

        self.ai = None
        if not is_player:
            self.ai = SimpleAI(self, galaxy)

    def tick(self):
        # ✅ NOWY: Tick transportów
        self.military_manager.tick()
        self.transport_manager.tick()
        
        if not self.is_player:
            self.ai.tick()
            
        for p in self.planets:
            if p.owner is not self:
                print(" PLANET OWNER DESYNC", p)
        
    def status(self, galaxy):
        print(f"=== {self.name} STATUS ===")
        
        # Pokaż aktywne transporty
        if self.transport_manager.transports:
            print(f"Active transports: {len(self.transport_manager.transports)}")
            for t in self.transport_manager.transports:
                source_sys, source_orbit = t.source.get_location(galaxy)
                target_sys, target_orbit = t.target.get_location(galaxy)
               # print(f"  S{source_orbit}→S{target_orbit}: {t.time_remaining}/{t.time_total} turns")
        
        for p in self.planets:
            system, orbit = p.get_location(galaxy)
            pos = f"System {system.star.type if system else '??'}, Orbit {orbit}" 
            print(f"Planet {id(p)} @ {pos}: Population={p.population.size:.1f}, Buildings={p.buildings_summary()}")

    def add_planet(self, planet):
        if planet not in self.planets:
            self.planets.append(planet)
            planet.owner = self
            
    def can_colonize(self, planet):
        return not planet.colonized
        
    def create_transport(self, source, target, cargo, transport_type="resources"):
        """Wrapper dla tworzenia transportu"""
        return self.transport_manager.create_transport(source, target, cargo, transport_type)