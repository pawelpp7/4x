
def test_full_colonization_and_development_flow():
    # --- IMPORTY ---
    from galaxy.galaxy import Galaxy
    from empire.empire import Empire
    from buildings.SpacePort import SpacePort
    from buildings.PopulationHub import PopulationHub

    # --- GALAXY ---
    galaxy = Galaxy(system_count=1, size=200)
    system = galaxy.systems[0]["system"]

    # --- EMPIRE ---
    empire = Empire("Test Empire", (255,255,255), galaxy, is_player=True, energy=200)

    # --- PLANETY ---
    source_planet = system.planets[0]
    target_planet = system.planets[1]

    # ręcznie skolonizuj planetę-źródło
    source_planet.colonized = True
    source_planet.owner = empire
    source_planet.population.size = 10.0
    empire.planets.append(source_planet)

    # daj zasoby PLANECIE ŹRÓDŁOWEJ
    for r in ["biomass", "compounds", "fluidics"]:
        source_planet.storage[r] = 100.0

    # --- SPACE PORT ---
    spaceport = SpacePort()

    ok, sources = spaceport.can_build(target_planet, empire)
    assert ok
    assert source_planet in sources

    ok, msg = spaceport.build(target_planet, empire, source_planet)
    assert ok
    assert target_planet.colonization_state == "colonizing"

    # --- SYMULACJA TICKÓW KOLONIZACJI ---
    for _ in range(int(target_planet.colonization_time)):
        target_planet.tick()

    assert target_planet.colonized is True
    assert target_planet.population.size > 0.0
    empire.planets.append(target_planet)

    # --- POPULATION HUB ---
    hub = PopulationHub()
    hex0 = target_planet.hex_map.hexes[0]

    ok, msg = hub.build(target_planet, hex0)
    assert ok

    # --- ROZWÓJ POPULACJI ---
    pop_before = target_planet.population.size
    for _ in range(10):
        target_planet.tick()

    assert target_planet.population.size > pop_before

if __name__ == "__main__":
    test_full_colonization_and_development_flow()
