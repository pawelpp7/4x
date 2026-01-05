# render/planet_view.py
import pygame
import math

HEX_SIZE = 18
SOURCE_ICONS = {
    "temperature": ("H", (220, 80, 60)),   # Heat
    "cold":        ("C", (80, 140, 220)),  # Cold
    "height":      ("^", (180, 180, 180)), # Mountains
    "erosion":     ("~", (60, 100, 180)),  # Water / basins
    "life":        ("+", (80, 200, 80)),   # Life
    "toxic":       ("X", (160, 100, 160)), # Toxic
}

BUILDING_SYMBOLS = {
    "Population Hub": ("P", (240, 240, 240)),
    "Biomass Mine":   ("B", (80, 200, 120)),
    "Fluidics Mine":  ("F", (80, 120, 255)),
    "Thermal Mine":   ("T", (255, 120, 80)),
}

RESOURCE_COLORS = {
    "thermal":   (255, 100, 60),   # ogień
    "cryo":      (80, 160, 255),   # lód
    "solids":    (160, 160, 160),  # minerały
    "fluidics":  (80, 120, 255),   # płyny
    "biomass":   (80, 200, 120),   # bio
    "compounds": (180, 120, 200),  # chemia
}


NEGATIVE_ICON_COLOR = (80, 120, 200)

def hex_to_pixel(q, r, center):
    x = HEX_SIZE * (3/2 * q)
    y = HEX_SIZE * (math.sqrt(3) * (r + q / 2))
    return int(center[0] + x), int(center[1] + y)

def hex_color(hex, overlay):
    if overlay == 0:  # TEMPERATURA
        r = clamp(128 + hex.temperature * 80)
        g = 80
        b = 80
        return (r, g, b)

    if overlay == 1:  # HEIGHT
        r = 60
        g = clamp(128 + hex.height * 80)
        b = 60
        return (r, g, b)

    if overlay == 2:  # LIFE
        r = 60
        g = clamp(100 + hex.life * 80)
        b = 60
        return (r, g, b)

    if overlay == 3:  # RESOURCES (DOMINUJĄCY)
        if not hex.resources:
            return (70, 70, 90)

        # 🔹 wybór dominującego zasobu
        res, val = max(hex.resources.items(), key=lambda x: x[1])

        base = RESOURCE_COLORS.get(res, (120, 120, 120))

        # 🔹 intensywność wg wartości
        scale = min(1.0, val)
        r = clamp(base[0] * (0.5 + scale * 0.5))
        g = clamp(base[1] * (0.5 + scale * 0.5))
        b = clamp(base[2] * (0.5 + scale * 0.5))

        return (r, g, b)

    return (100, 100, 100)


def clamp(x, a=0, b=255):
    return max(a, min(b, int(x)))


def draw_hex(screen, pos, color,planet ,selected=False ):
    x, y = pos
    points = []

    for i in range(6):
        angle = math.pi / 3 * i
        px = x + HEX_SIZE * math.cos(angle)
        py = y + HEX_SIZE * math.sin(angle)
        points.append((px, py))

    pygame.draw.polygon(screen, color, points)

    if planet.colonization_state == "colonizing":
        border_color = (240, 220, 120)
    elif planet.owner:
        border_color = planet.owner.color
    else:
        border_color = (80, 80, 80)


    border = (255, 255, 255) if selected  else  border_color
    
    width = 3 if selected else 1
    pygame.draw.polygon(screen, border, points, width)


def draw_planet(screen, planet, center, selected_hex, overlay_mode):
    screen.fill((5, 5, 10))

    for hex in planet.hex_map.hexes:
        pos = hex_to_pixel(hex.q, hex.r, center)
        color = hex_color(hex, overlay_mode)
        draw_hex(screen, pos, color,planet, hex is selected_hex)
        draw_source_icons(screen, planet, hex, pos)
        draw_hex_buildings(screen, hex, pos)
    draw_population_panel(screen, planet)


            


def pick_hex(planet, mouse_pos, center):
    mx, my = mouse_pos

    for hex in planet.hex_map.hexes:
        hx, hy = hex_to_pixel(hex.q, hex.r, center)
        dx = mx - hx
        dy = my - hy

        if dx * dx + dy * dy < HEX_SIZE * HEX_SIZE:
            return hex

    return None


def draw_source_icons(screen, planet, hex, pos):
    sources = planet.sources_at(hex.q, hex.r)
    if not sources:
        return

    font = pygame.font.SysFont(None, 18)

    # przesunięcia, żeby ikony się nie nakładały
    offsets = [(-6, -6), (6, -6), (0, 6)]

    for i, src in enumerate(sources):
        symbol, color = SOURCE_ICONS.get(
            src.icon, ("?", (200, 200, 200))
        )

        img = font.render(symbol, True, color)
        dx, dy = offsets[i % len(offsets)]
        rect = img.get_rect(center=(pos[0] + dx, pos[1] + dy))
        screen.blit(img, rect)

def building_symbol(building):
    return BUILDING_SYMBOLS.get(
        building.name,
        (building.name[0].upper(), (220, 220, 220))
    )
def draw_hex_buildings(screen, hex, pos):
    font = pygame.font.SysFont(None, 14)
    x, y = pos

    offset_y = -10

    # major building (jeśli kiedyś dodasz)
    if getattr(hex, "building_major", None):
        symbol, color = building_symbol(hex.building_major)
        img = font.render(symbol, True, color)
        screen.blit(img, (x - 6, y + offset_y))
        offset_y += 12

    # small buildings
    for b in hex.buildings_small:
        symbol, color = building_symbol(b)
        img = font.render(symbol, True, color)
        screen.blit(img, (x - 6, y + offset_y))
        offset_y += 10



def draw_population_panel(screen, planet):
    font = pygame.font.SysFont(None, 18)
    big = pygame.font.SysFont(None, 22)

    x = screen.get_width() - 220
    y = 20

    pygame.draw.rect(screen, (20, 20, 40), (x - 10, y - 10, 210, 220))
    pygame.draw.rect(screen, (80, 80, 120), (x - 10, y - 10, 210, 220), 1)

    screen.blit(big.render("Population", True, (255, 255, 255)), (x, y))
    y += 26

    screen.blit(
        font.render(f"Size: {planet.population.size:.2f}", True, (220, 220, 220)),
        (x, y)
    )
    y += 20

    for stat, val in planet.population.stats.items():
        bar_len = int(val * 8)
        bar = "█" * bar_len
        txt = f"{stat[:6].upper():6} {bar}"
        screen.blit(font.render(txt, True, (200, 200, 200)), (x, y))
        y += 16

def draw_build_menu(screen, planet, hex, items):
    font = pygame.font.SysFont(None, 20)
    big = pygame.font.SysFont(None, 26)

    w, h = screen.get_size()
    x = w // 2 - 160
    y = h // 2 - 200

    # tło
    pygame.draw.rect(screen, (15, 15, 30), (x, y, 320, 360))
    pygame.draw.rect(screen, (120, 120, 180), (x, y, 320, 360), 2)

    screen.blit(big.render("BUILD", True, (255, 255, 255)), (x + 110, y + 10))
    y += 50

    if not items:
        screen.blit(font.render("No buildings available", True, (180, 80, 80)), (x + 60, y))
        return

    for i, b in enumerate(items):
        txt = f"{i+1}. {b.name}"
        screen.blit(font.render(txt, True, (220, 220, 220)), (x + 20, y))
        y += 28

        # koszt
        cost_y = y
        for res, val in b.cost.items():
            c = (180, 180, 180) if planet.storage.get(res, 0) >= val else (200, 80, 80)
            screen.blit(
                font.render(f"   {res}: {val}", True, c),
                (x + 40, cost_y)
            )
            cost_y += 18

        y = cost_y + 6
