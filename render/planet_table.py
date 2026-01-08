import pygame

RES_KEYS = ["thermal", "cryo", "solids", "fluidics", "biomass", "compounds"]
def draw_planet_hex_table(screen, planet, font, mouse_pos, scroll_y, sort_key):
    x = 20
    y0 = 20
    row_h = 22

    build_buttons = []
    header_clicks = []

    # === HEADER ===
    headers = [
        ("HEX", None),
        ("TEMP", "temperature"),
        ("LIFE", "life"),
        ("THERM", "thermal"),
        ("CRYO", "cryo"),
        ("SOL", "solids"),
        ("FLU", "fluidics"),
        ("BIO", "biomass"),
        ("CMP", "compounds"),
    ]

    cx = x
    for name, key in headers:
        img = font.render(name, True, (220,220,240))
        screen.blit(img, (cx, y0))
        if key:
            header_clicks.append((key, pygame.Rect(cx, y0, 50, row_h)))
        cx += 50

    y = y0 + row_h

    # === SORT ===
    hexes = planet.hex_map.hexes[:]
    if sort_key:
        if sort_key in ("temperature", "life"):
            hexes.sort(key=lambda h: getattr(h, sort_key), reverse=True)
        else:
            hexes.sort(key=lambda h: h.resources.get(sort_key, 0), reverse=True)

    # === ROWS ===
    for h in hexes:
        ry = y - scroll_y
        content_top = y0 + row_h
        content_bottom = screen.get_height() - 10

        if ry < content_top or ry > content_bottom:
            y += row_h
            continue



        line = f"({h.q},{h.r})"
        screen.blit(font.render(line, True, (200,200,200)), (x, ry))

        vals = [
            f"{h.temperature:+.2f}",
            f"{h.life:+.2f}",
            f"{h.resources.get('energy',0):.1f}",
            f"{h.resources.get('gases',0):.1f}",
            f"{h.resources.get('minerals',0):.1f}",
            f"{h.resources.get('water',0):.1f}",
            f"{h.resources.get('organics',0):.1f}",
            f"{h.resources.get('rare_elements',0):.1f}",
        ]

        cx = x + 50
        for v in vals:
            screen.blit(font.render(v, True, (200,200,200)), (cx, ry))
            cx += 50

        # === BUILD BUTTON ===
        bx, by, bw, bh = x + 470, ry, 60, 18
        mx, my = mouse_pos
        hovered = bx <= mx <= bx+bw and by <= my <= by+bh

        color = (140,180,240) if hovered else (100,140,200)
        pygame.draw.rect(screen, color, (bx, by, bw, bh))
        screen.blit(font.render("BUILD", True, (20,20,30)), (bx+6, by+1))

        build_buttons.append((h, (bx, by, bw, bh)))
        y += row_h

    return build_buttons, header_clicks
