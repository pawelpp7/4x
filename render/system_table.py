def draw_system_table(screen, system, font, sort_key="pop"):
    x, y = 20, 20
    row_h = 22
    clicks = []


    planets = system.planets[:]

    if sort_key == "pop":
        planets.sort(key=lambda p: p.population.size, reverse=True)
    elif sort_key == "energy":
        planets.sort(key=lambda p: p.energy_delta(), reverse=True)
    elif sort_key == "res":
        planets.sort(key=lambda p: sum(p.storage.values()), reverse=True)

    header = "PL | POP | EN | TH SO BI FL CR EX"
    screen.blit(font.render(header, True, (220,220,240)), (x, y))
    y += row_h

    for i, p in enumerate(planets):
        line = (
            f"{i:^2} "
            f"{p.population.size:5.1f} "
            f"{p.energy_delta():+5.2f} "
            f"{p.storage['thermal']:2.0f} "
            f"{p.storage['solids']:2.0f} "
            f"{p.storage['biomass']:2.0f} "
            f"{p.storage['fluidics']:2.0f} "
            f"{p.storage['cryo']:2.0f} "
            f"{p.storage['exotics']:2.0f}"
        )
        screen.blit(font.render(line, True, (200,200,200)), (x, y))
        y += row_h
    return clicks