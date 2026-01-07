# render/system_view.py
import pygame
import math

STAR_COLOR = (255, 220, 120)
PLANET_COLOR = (150, 180, 255)
ORBIT_COLOR = (60, 60, 80)

def draw_system(screen, system, center):
    cx, cy = center
    screen.fill((5, 5, 10))

    # gwiazda ZAWSZE wg typu
    pygame.draw.circle(screen, STAR_COLOR, center, 18)

    orbit_step = 45
    planet_count = len(system.planets)

    for i, planet in enumerate(system.planets):
        radius = orbit_step * (i + 1)
        pygame.draw.circle(screen, ORBIT_COLOR, center, radius, 1)

        angle = i * 2 * math.pi / planet_count
        px = int(cx + math.cos(angle) * radius)
        py = int(cy + math.sin(angle) * radius)

        color = planet_status_color(planet)
        pygame.draw.circle(screen, color, (px, py), 8)





def planet_status_color(planet):
    if getattr(planet, "colonization_state", None) == "colonizing":
        return (240, 220, 120)  # żółta
    
    if not planet.colonized or not planet.owner:
        return planet_color(planet)

    if planet.colonized:
        return planet.owner.color

    return (120, 120, 160)  # nieskolonizowana


def planet_color(planet):
    t = planet.temperature
    l = planet.life
    h = planet.height

    r = int(120 + 80 * max(0, t))
    b = int(120 + 80 * max(0, -t))
    g = int(120 + 60 * max(0, l))

    return (
        min(255, r),
        min(255, g),
        min(255, b)
    )

def planet_tooltip_data(planet, orbit):
    return [
        f"Orbit: {orbit}",
        f"Colonized: {'YES' if planet.colonized else 'NO'}",
        f"Owner: {planet.owner.name if planet.owner else 'None'}",
        f"Population: {planet.population.size:.1f}",
        f"Primary: {planet.primary_resource.upper()}",
    ]


