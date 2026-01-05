# render/draw_galaxy.py
import pygame
from render.colors import STAR_COLORS, BACKGROUND

SYSTEM_RADIUS = 6

LINK_COLOR = (80, 80, 120)

def draw_galaxy(screen, galaxy):
    screen.fill(BACKGROUND)

    # połączenia
    for s in galaxy.systems:
        for t in s["links"]:
            pygame.draw.line(
                screen,
                LINK_COLOR,
                (int(s["x"]), int(s["y"])),
                (int(t["x"]), int(t["y"])),
                1
            )

    # systemy
    for s in galaxy.systems:
        x = int(s["x"])
        y = int(s["y"])

        system = s["system"]
        color = system_color(system)

        pygame.draw.circle(screen, color, (x, y), SYSTEM_RADIUS)




def pick_system(galaxy, mouse_pos):
    mx, my = mouse_pos

    for s in galaxy.systems:
        dx = s["x"] - mx
        dy = s["y"] - my
        if dx * dx + dy * dy < SYSTEM_RADIUS ** 2:
            return s["system"]

    return None

def system_color(system):
    owners = set(p.owner for p in system.planets if p.colonized)

    if not owners:
        return (180, 180, 180)  # pusty

    if len(owners) > 1:
        return (255, 120, 120)  # konflikt

    owner = owners.pop()
    return owner.color
