def draw_galaxy_table(screen, galaxy, font):
    clicks = []

    x, y = 20, 20
    row_h = 22

    for entry in galaxy.systems:
        system = entry["system"]

        rect = (x, y, 360, row_h)
        clicks.append((system, rect))

        screen.blit(font.render(system.star.type, True, (200,200,200)), (x, y))
        y += row_h

    return clicks
