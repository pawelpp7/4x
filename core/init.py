from buildings.EmpireSpacePort import EmpireSpacePort


def init_start_planet(empire, system_entry):
    system = system_entry["system"]
    planet = system.planets[0]

    free_hex = min(
        planet.hex_map.hexes,
        key=lambda h: abs(h.q) + abs(h.r)
    )

    if not free_hex:
        raise RuntimeError("No free hex for starting EmpireSpacePort")

    esp = EmpireSpacePort()
    esp.owner = empire

    ok, msg = esp.build(planet, free_hex)
    if not ok:
        raise RuntimeError(msg)

    # 🔥 TO JEST KLUCZ
    if planet not in empire.planets:
        empire.planets.append(planet)

    planet.owner = empire
    planet.colonized = True

    print(f"INIT {empire.name}: {msg}")
