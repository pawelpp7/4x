def draw_system_table(screen, system, font, sort_key="pop"):
    x, y = 20, 20
    row_h = 22
    clicks = []

    planets = system.planets[:]

    if sort_key == "pop":
        planets.sort(key=lambda p: p.population.size if p.population else 0, reverse=True)
    elif sort_key == "energy":
        planets.sort(key=lambda p: p.energy_delta() if p.colonized else 0, reverse=True)
    elif sort_key == "res":
        planets.sort(key=lambda p: sum(p.storage.values()) if p.colonized else 0, reverse=True)

    header = "PL | POP | EN | TH SO BI FL CR EX"
    screen.blit(font.render(header, True, (220,220,240)), (x, y))
    y += row_h

    for i, p in enumerate(planets):
        # bezpieczne pobieranie wartości dla nieskolonizowanych planet
        pop = p.population.size if p.population else 0.0
        energy = p.energy_delta() if p.colonized and p.population else 0.0
        
        line = (
            f"{i:^2} "
            f"{pop:5.1f} "
            f"{energy:+5.2f} "
            f"{p.storage.get('energy', 0):2.0f} "
            f"{p.storage.get('minerals', 0):2.0f} "
            f"{p.storage.get('organics', 0):2.0f} "
            f"{p.storage.get('water', 0):2.0f} "
            f"{p.storage.get('gases', 0):2.0f} "
            f"{p.storage.get('rare_elements', 0):2.0f}"
        )
        
        color = (200, 200, 200)
        if p.colonized and p.owner:
            color = p.owner.color
        
        screen.blit(font.render(line, True, color), (x, y))
        
        # kliknięcie na planetę
        rect = (x, y, 400, row_h)
        clicks.append((p, rect))
        
        y += row_h
        
    return clicks