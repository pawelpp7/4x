from galaxy.galaxy import Galaxy
from empire.empire import Empire
from core.init import init_start_planet
from military.PlanetaryInvasion import PlanetaryInvasion


def test_invasion_capture():
    galaxy = Galaxy(system_count=2, size=300)
    attacker = Empire("Attacker", (80, 80, 200), galaxy)
    defender = Empire("Defender", (200, 80, 80), galaxy)
    galaxy.empires.extend([attacker, defender])

    # Initialize defender start planet
    init_start_planet(defender, galaxy.systems[0])
    target = galaxy.systems[0]["system"].planets[0]

    assert target.owner == defender

    invasion = PlanetaryInvasion(attacker, target, invasion_force=[])
    invasion.tick()

    assert target.owner == attacker
    assert target in attacker.planets
    assert target not in defender.planets
