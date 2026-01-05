# main.py
import pygame
import math

from galaxy.galaxy import Galaxy
from render.draw_galaxy import draw_galaxy, pick_system, system_tooltip_data
from render.system_view import draw_system, planet_tooltip_data
from render.planet_view import draw_planet, hex_tooltip_data, pick_hex, draw_build_menu
from empire.empire import Empire
from ai.simple_ai import SimpleAI
from buildings.PopulationHub import PopulationHub
from buildings.SpacePort import SpacePort
from buildings.production import ResourceBuilding

GALAXY_VIEW = 0
SYSTEM_VIEW = 1
PLANET_VIEW = 2
BUILD_MENU = 3

OVERLAY_TEMP = 0
OVERLAY_HEIGHT = 1
OVERLAY_LIFE = 2
OVERLAY_RES = 3
OVERLAY_PRODUCTION = 4
OVERLAY_POPULATION = 5



WIDTH, HEIGHT = 1000, 1000
TICK_MS = 1000

def main():
    build_menu_hex = None
    build_menu_items = []
    planet_positions = []
    hovered_system = None
    hovered_planet = None
    hovered_hex = None

    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 18)

    galaxy = Galaxy(system_count=40, size=900)
    empire = Empire("Player", (80, 200, 120), galaxy, is_player=True)
    ai_empire = Empire("AI Empire", (200, 70, 180), galaxy)

    galaxy.empires.extend([empire, ai_empire])

    # 🔨 NOWA LOGIKA - startowa planeta dla gracza
    start_system = galaxy.systems[0]["system"]
    start_planet = start_system.planets[0]

    spaceport = SpacePort()
    spaceport.owner = empire
    start_hex = start_planet.hex_map.hexes[0]
    
    success, msg = spaceport.build(start_planet, start_hex)
    if success:
        print(f"INIT Player starting planet: {msg}")
    else:
        print(f"INIT Failed to initialize starting planet: {msg}")

    prod = galaxy.produce()
    print("=== GALACTIC PRODUCTION (1 TICK) ===")
    for res, val in sorted(prod.items()):
        print(f"{res:10s}: {val:8.2f}")

    current_view = GALAXY_VIEW
    current_system = None
    current_planet = None
    selected_hex = None
    overlay_mode = OVERLAY_TEMP

    last_tick = pygame.time.get_ticks()
    running = True

    while running:
        # ================= EVENTS =================
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:

                # === GLOBAL ===
                if event.key == pygame.K_ESCAPE:
                    if current_view == PLANET_VIEW:
                        current_view = SYSTEM_VIEW
                        selected_hex = None
                    elif current_view == SYSTEM_VIEW:
                        current_view = GALAXY_VIEW
                    elif current_view == BUILD_MENU:
                        current_view = PLANET_VIEW

                # === PLANET VIEW ===
                if current_view == PLANET_VIEW:

                    if event.key == pygame.K_1:
                        overlay_mode = OVERLAY_TEMP
                    elif event.key == pygame.K_2:
                        overlay_mode = OVERLAY_HEIGHT
                    elif event.key == pygame.K_3:
                        overlay_mode = OVERLAY_LIFE
                    elif event.key == pygame.K_4:
                        overlay_mode = OVERLAY_RES
                    elif event.key == pygame.K_5:
                        overlay_mode = OVERLAY_PRODUCTION
                    elif event.key == pygame.K_6:
                        overlay_mode = OVERLAY_POPULATION


                    # 🔨 OTWARCIE MENU BUDOWY
                    elif event.key == pygame.K_b and selected_hex:
                        build_menu_hex = selected_hex
                        build_menu_items = get_available_buildings(current_planet, selected_hex)
                        current_view = BUILD_MENU

                # === BUILD MENU ===
                elif current_view == BUILD_MENU:
                    idx = event.key - pygame.K_1
                    if 0 <= idx < len(build_menu_items):
                        building = build_menu_items[idx]
                        building.owner = empire
                        
                        # 🔨 NOWA LOGIKA - używamy build()
                        success, msg = building.build(current_planet, build_menu_hex)
                        
                        if success:
                            print(f"PLAYER {msg}")
                        else:
                            print(f"PLAYER Build failed: {msg}")
                        
                        current_view = PLANET_VIEW

            elif event.type == pygame.MOUSEBUTTONDOWN:

                if current_view == GALAXY_VIEW:
                    system = pick_system(galaxy, event.pos)
                    if system:
                        current_system = system
                        current_view = SYSTEM_VIEW

                elif current_view == SYSTEM_VIEW:
                    mx, my = pygame.mouse.get_pos()
                    cx, cy = WIDTH // 2, HEIGHT // 2
                    orbit_step = 45
                    for i, planet in enumerate(current_system.planets):
                        radius = orbit_step * (i + 1)
                        angle = i * 2 * math.pi / len(current_system.planets)
                        px = cx + math.cos(angle) * radius
                        py = cy + math.sin(angle) * radius
                        planet_positions.append((planet, (px, py), i))
                        if (mx - px) ** 2 + (my - py) ** 2 < 8 ** 2:
                            current_planet = planet
                            current_view = PLANET_VIEW
                            break


                elif current_view == PLANET_VIEW:
                    selected_hex = pick_hex(
                        current_planet,
                        event.pos,
                        (WIDTH // 2, HEIGHT // 2)
                    )


        # ================= TICK =================
        now = pygame.time.get_ticks()
        if now - last_tick >= TICK_MS:
            last_tick = now
            galaxy.tick()

        # ================= RENDER =================
        screen.fill((0, 0, 0))
        screen.blit(font.render(
            f"ENERGY: {empire.storage['energy']:.1f} ({empire.energy_last:+.1f}/t)",
            True, (120,220,120) if empire.energy_last >= 0 else (220,120,120)
        ), (10, 10))
        if current_view == GALAXY_VIEW:
            draw_galaxy(screen, galaxy)
            
            hovered = pick_system(galaxy, pygame.mouse.get_pos())
            if hovered:
                lines = system_tooltip_data(hovered)
                mx, my = pygame.mouse.get_pos()
                y = my + 10
                for l in lines:
                    img = font.render(l, True, (220,220,220))
                    screen.blit(img, (mx + 10, y))
                    y += 16

        elif current_view == SYSTEM_VIEW:
            draw_system(screen, current_system, (WIDTH // 2, HEIGHT // 2))
            mx, my = pygame.mouse.get_pos()
            for planet, (px,py), orbit in planet_positions:
                if (mx-px)**2 + (my-py)**2 < 8**2:
                    lines = planet_tooltip_data(planet, orbit)
                    y = my + 10
                    for l in lines:
                        screen.blit(font.render(l, True, (220,220,220)), (mx+10, y))
                        y += 16

        elif current_view == PLANET_VIEW:
            draw_planet(
                screen,
                current_planet,
                (WIDTH // 2, HEIGHT // 2),
                selected_hex,
                overlay_mode
            )
            hover_hex = pick_hex(current_planet, pygame.mouse.get_pos(), (WIDTH//2, HEIGHT//2))
            if hover_hex:
                lines = hex_tooltip_data(hover_hex, current_planet)
                mx, my = pygame.mouse.get_pos()
                y = my + 10
                for l in lines:
                    screen.blit(font.render(l, True, (230,230,230)), (mx+10, y))
                    y += 16




            # === STORAGE ===
            y = 150
            screen.blit(font.render("STORAGE:", True, (200, 200, 200)), (10, y))
            y += 20
            for res, val in current_planet.storage.items():
                img = font.render(f"{res.upper()}: {val:.1f}", True, (180, 180, 220))
                screen.blit(img, (10, y))
                y += 18

            # === OVERLAY LABELS ===
            labels = ["1 TEMP", "2 HEIGHT", "3 LIFE", "4 RES", "5 PROD", "6 POP"]
            for i, txt in enumerate(labels):
                img = font.render(txt, True, (180, 180, 180))
                screen.blit(img, (10, HEIGHT - 20 * (len(labels) - i)))

            # === BUILD KEYS ===
            build_labels = [
                "B – Build Menu",
            ]

            for i, txt in enumerate(build_labels):
                img = font.render(txt, True, (200, 200, 200))
                screen.blit(img, (WIDTH - 160, HEIGHT - 20 * (len(build_labels) - i)))

            # === HEX INFO ===
            if selected_hex:
                lines = [
                    f"TEMP: {selected_hex.temperature:.2f}",
                    f"HEIGHT: {selected_hex.height:.2f}",
                    f"LIFE: {selected_hex.life:.2f}",
                    f"RES: {selected_hex.resources}",
                ]
                for i, text in enumerate(lines):
                    img = font.render(text, True, (200, 200, 200))
                    screen.blit(img, (10, 10 + i * 18))

        elif current_view == BUILD_MENU:
            draw_planet(
                screen,
                current_planet,
                (WIDTH // 2, HEIGHT // 2),
                build_menu_hex,
                overlay_mode
            )

            draw_build_menu(
                screen,
                current_planet,
                build_menu_hex,
                build_menu_items
            )

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

from buildings.registry import BUILDINGS

def get_available_buildings(planet, hex):
    """Zwraca listę budynków możliwych do zbudowania na tym hexie"""
    items = []

    for name, factory in BUILDINGS.items():
        building = factory()

        # Sprawdź czy można zbudować na hexie
        if not hex.can_build(building, planet):
            continue

        # Sprawdź czy stać
        if not building.can_afford(planet):
            continue

        # SpacePort tylko dla nieskolonizowanych
        if building.name == "Space Port" and planet.colonized:
            continue

        items.append(building)

    return items

if __name__ == "__main__":
    main()