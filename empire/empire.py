from ai.simple_ai import SimpleAI

class Empire:
    def __init__(self, name, color, galaxy, is_player=False,energy=200):
        self.name = name
        self.color = color
        self.galaxy = galaxy
        self.energy=energy
        self.is_player = is_player
        self.energy_last=100.0
        self.planets = []
        
        for p in self.planets:
            p.owner = self
            p.colonized = True
            self.planets.append(p)



        self.ai = None
        if not is_player:
            self.ai = SimpleAI(self, galaxy)


    def tick(self):
        if not self.is_player:
            self.ai.tick()
        for p in self.planets:
            if p.owner is not self:
                print("❌ PLANET OWNER DESYNC", p)

            
        
    def status(self, galaxy):
        print(f"=== {self.name} STATUS ===")
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
