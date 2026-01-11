# main.py - COMPLETE VERSION WITH TRANSPORT
from buildings.EmpireSpacePort import EmpireSpacePort
from core.init import init_start_planet
import pygame
import math
from render.build_menu import (
    draw_simple_build_menu,
    handle_build_menu_scroll,
    BuildMenuState
)
from galaxy.galaxy import Galaxy
from render.draw_galaxy import draw_galaxy, pick_system, system_tooltip_data
from render.system_view import draw_system, planet_tooltip_data
from render.planet_view import draw_planet, hex_tooltip_data, pick_hex, draw_build_menu
from empire.empire import Empire
from ai.simple_ai import SimpleAI
from buildings.PopulationHub import PopulationHub
from buildings.SpacePort import SpacePort
from render.galaxy_table import draw_galaxy_table
from render.system_table import draw_system_table
from render.planet_table import draw_planet_hex_table

from render.transport_view import (
    draw_transport_panel,
    draw_transport_creation_menu,
    draw_cargo_selection_menu
)

from render.military_view import (
    draw_military_panel,
    draw_military_production_menu,
    draw_garrison_detail_view
)
# ============================================
# VIEW STATES
# ============================================
GALAXY_VIEW = 0
SYSTEM_VIEW = 1
PLANET_VIEW = 2
BUILD_MENU = 3
SELECT_SOURCE = 4
TRANSPORT_TARGET_SELECT = 5  
TRANSPORT_CARGO_SELECT = 6   
MILITARY_RECRUIT_MENU = 7
MILITARY_GARRISON_VIEW = 8



LEFT_PANEL_W = 550

# ============================================
# OVERLAY MODES
# ============================================
OVERLAY_TEMP = 0
OVERLAY_HEIGHT = 1
OVERLAY_LIFE = 2
OVERLAY_RES = 3
OVERLAY_PRODUCTION = 4
OVERLAY_POPULATION = 5

WIDTH, HEIGHT = 1600, 1000
TICK_MS = 1000

def main():
    build_menu_hex = None
    build_menu_items = []
    planet_positions = []
    table_clicks = []
    build_buttons = []
    header_clicks = []
    sort_key = "energy"
    colonization_mode = False
    colonization_target = None
    colonization_sources = []
    
    transport_source_planet = None
    transport_target_planet = None
    clickable_planets = []
    clickable_cargo = []
    clickable_units = []

    build_menu_hex = None
    build_menu_items = []
    build_menu_state = BuildMenuState()  # ✅ Użyj obiektu zamiast oddzielnych zmiennych
    clickable_build_items = []
    clickable_build_tabs = []
    
    hovered_system = None
    hovered_planet = None
    hovered_hex = None
    
    hex_table_scroll = 0
    HEX_ROW_H = 22
    HEX_TABLE_Y = 20
    HEX_TABLE_H = HEIGHT - 40

    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 18)

    galaxy = Galaxy(system_count=40, size=900)

    empire = Empire("Player", (80, 200, 120), galaxy, is_player=True)
    ai_empire = Empire("AI Empire", (200, 70, 180), galaxy)

    galaxy.empires.extend([empire, ai_empire])

    # ✅ START PLAYER
    init_start_planet(empire, galaxy.systems[0])

    # ✅ START AI (INNY SYSTEM!)
    init_start_planet(ai_empire, galaxy.systems[1])

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
    paused = True

    while running:
        # ================= EVENTS =================
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
            elif event.type == pygame.MOUSEWHEEL:
                if current_view == BUILD_MENU:
                    # Scroll build menu
                    handle_build_menu_scroll(build_menu_state, event.y)
                    # Max scroll będzie zastosowany przy renderowaniu
                elif current_view == PLANET_VIEW:
                    # Existing hex table scroll
                    hex_table_scroll -= event.y * HEX_ROW_H
                    hex_table_scroll = max(0, min(hex_table_scroll, max_scroll))

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
                        build_menu_scroll = 0
                    elif current_view == TRANSPORT_TARGET_SELECT:
                        current_view = PLANET_VIEW
                        transport_source_planet = None
                    elif current_view == TRANSPORT_CARGO_SELECT:
                        current_view = PLANET_VIEW
                        transport_source_planet = None
                        transport_target_planet = None
                    elif current_view == MILITARY_RECRUIT_MENU:
                        current_view = PLANET_VIEW
                    elif current_view == MILITARY_GARRISON_VIEW:
                        current_view = PLANET_VIEW
                elif event.key == pygame.K_SPACE:
                    paused = not paused

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
                        

                    elif event.key == pygame.K_b and selected_hex:
                        build_menu_hex = selected_hex
                        build_menu_items = get_available_buildings(current_planet, selected_hex)
                        build_menu_scroll = 0  # Reset scroll
                        build_menu_category = None  # Reset filter
                        current_view = BUILD_MENU

                    elif event.key == pygame.K_t:
                        transport_source_planet = current_planet
                        current_view = TRANSPORT_TARGET_SELECT
                        
                    if event.key == pygame.K_m:
                        current_view = MILITARY_RECRUIT_MENU
                    if event.key == pygame.K_g:
                        current_view = MILITARY_GARRISON_VIEW

                # === BUILD MENU ===
                elif current_view == BUILD_MENU:
                    idx = event.key - pygame.K_1
                    if 0 <= idx < len(build_menu_items):
                        building = build_menu_items[idx]
                        
                        # === SPACE PORT → TRYB KOLONIZACJI ===
                        if building.name == "Space Port":
                            colonization_mode = True
                            colonization_target = current_planet
                            colonization_sources = find_valid_source_planets(empire, building)

                            if not colonization_sources:
                                print("No valid source planets for colonization!")
                                colonization_mode = False
                                current_view = PLANET_VIEW
                            else:
                                current_view = SELECT_SOURCE

                        # === NORMALNA BUDOWA ===
                        else:
                            building.owner = empire
                            success, msg = building.build(current_planet, build_menu_hex)

                            if success:
                                print(f"PLAYER {msg}")
                            else:
                                print(f"PLAYER Build failed: {msg}")

                            current_view = PLANET_VIEW
                            
                elif current_view == SELECT_SOURCE:
                    if event.key == pygame.K_ESCAPE:
                        colonization_mode = False
                        current_view = PLANET_VIEW
                    else:
                        idx = event.key - pygame.K_1
                        if 0 <= idx < len(colonization_sources):
                            source_planet = colonization_sources[idx]
                            spaceport = SpacePort()
                            spaceport.owner = empire

                            success, msg = spaceport.build(
                                colonization_target,
                                build_menu_hex,
                                source_planet
                            )

                            if success:
                                print(f"PLAYER {msg}")
                            else:
                                print(f"PLAYER Colonization failed: {msg}")

                            colonization_mode = False
                            current_view = PLANET_VIEW
                elif current_view == MILITARY_RECRUIT_MENU:
                    for unit_class, rect in clickable_units:
                        if rect.collidepoint(mx, my):
                            # Prosta wersja: od razu produkuj bez doktryny
                            success, msg = current_planet.military_manager.start_production(unit_class)
                            
                            if success:
                                print(f"PLAYER MILITARY: {msg}")
                            else:
                                print(f"PLAYER MILITARY FAILED: {msg}")
                            
                            current_view = PLANET_VIEW
                            break
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                
                # Header clicks (sorting)
                for key, rect in header_clicks:
                    if rect.collidepoint(mx, my):
                        sort_key = key
                        break

                # Build buttons
                for hex, rect in build_buttons:
                    bx, by, bw, bh = rect
                    if bx <= mx <= bx+bw and by <= my <= by+bh:
                        selected_hex = hex
                        current_view = BUILD_MENU

                # Table clicks
                for obj, rect in table_clicks:
                    x, y, w, h = rect
                    if x <= mx <= x + w and y <= my <= y + h:
                        # GALAXY → SYSTEM
                        if current_view == GALAXY_VIEW:
                            current_system = obj
                            current_view = SYSTEM_VIEW
                        # SYSTEM → PLANET
                        elif current_view == SYSTEM_VIEW:
                            current_planet = obj
                            current_view = PLANET_VIEW
                        # PLANET → BUILD
                        elif current_view == PLANET_VIEW:
                            build_menu_hex = obj
                            build_menu_items = get_available_buildings(current_planet, obj)
                            current_view = BUILD_MENU

                # ✅ NOWE - TRANSPORT TARGET SELECT
                if current_view == TRANSPORT_TARGET_SELECT:
                    for planet, rect in clickable_planets:
                        if rect.collidepoint(mx, my):
                            transport_target_planet = planet
                            current_view = TRANSPORT_CARGO_SELECT
                            break

                # ✅ NOWE - TRANSPORT CARGO SELECT
                elif current_view == TRANSPORT_CARGO_SELECT:
                    for cargo_item, rect in clickable_cargo:
                        if rect.collidepoint(mx, my):
                            # Utwórz transport
                            if cargo_item == "population":
                                cargo = 2.0
                                success, msg = empire.create_transport(
                                    transport_source_planet,
                                    transport_target_planet,
                                    cargo,
                                    "population"
                                )
                            else:
                                cargo = {cargo_item: 50.0}
                                success, msg = empire.create_transport(
                                    transport_source_planet,
                                    transport_target_planet,
                                    cargo,
                                    "resources"
                                )
                            
                            if success:
                                print(f"PLAYER TRANSPORT: {msg}")
                            else:
                                print(f"PLAYER TRANSPORT FAILED: {msg}")
                            
                            current_view = PLANET_VIEW
                            transport_source_planet = None
                            transport_target_planet = None
                            break

                # Galaxy click
                if current_view == GALAXY_VIEW:
                    system = pick_system(galaxy,(event.pos[0] - LEFT_PANEL_W, event.pos[1]))
                    if system:
                        current_system = system
                        current_view = SYSTEM_VIEW

                # System click
                elif current_view == SYSTEM_VIEW:
                    mx, my = pygame.mouse.get_pos()
                    cx = LEFT_PANEL_W + (WIDTH - LEFT_PANEL_W) // 2
                    cy = HEIGHT // 2
                    orbit_step = 45

                    planet_positions.clear()

                    for i, planet in enumerate(current_system.planets):
                        radius = orbit_step * (i + 1)
                        angle = i * 2 * math.pi / max(1, len(current_system.planets))
                        px = cx + math.cos(angle) * radius
                        py = cy + math.sin(angle) * radius
                        planet_positions.append((planet, (px, py), i))

                        if (mx - px) ** 2 + (my - py) ** 2 < 8 ** 2:
                            current_planet = planet
                            current_view = PLANET_VIEW
                            break

                # Planet click
                elif current_view == PLANET_VIEW:
                    planet_center = (
                        LEFT_PANEL_W + (WIDTH - LEFT_PANEL_W) // 2,
                        HEIGHT // 2
                    )
                    selected_hex = pick_hex(
                        current_planet,
                        (event.pos[0], event.pos[1]),
                        planet_center
                    )
                elif current_view == BUILD_MENU:

                    if current_view == BUILD_MENU:
                        if event.button == 4 or event.button == 5: 
                            continue
                        # Taby
                        for category, rect in clickable_build_tabs:
                            if rect.collidepoint(mx, my):
                                print(f"DEBUG: Clicked tab {category}")  
                                build_menu_state.category_filter = category
                                build_menu_state.scroll = 0
                                break
                        
                        # Budynki
                        for building, rect in clickable_build_items:
                            if rect.collidepoint(mx, my):
                                print(f"DEBUG: Clicked building {building.name} at {rect}")  
                                building.owner = empire
                                success, msg = building.build(current_planet, build_menu_hex)
                                
                                if success:
                                    print(f"PLAYER BUILD: {msg}")
                                else:
                                    print(f"PLAYER BUILD FAILED: {msg}")
                                
                                current_view = PLANET_VIEW
                                build_menu_state.scroll = 0
                                break
                            
                if current_view == MILITARY_RECRUIT_MENU:
                    from military.units import get_available_units

                    available_units = get_available_units(current_planet.military_level)

                    for i, unit_cls in enumerate(available_units):
                        rect = pygame.Rect(50, 120 + i * 60, 300, 50)

                        if rect.collidepoint(mx,my):
                            unit = unit_cls(owner=current_planet.owner)

                            # koszt (jeśli masz)
                            if current_planet.resources["metal"] >= unit.cost:
                                current_planet.resources["metal"] -= unit.cost
                                current_planet.military_units.append(unit)

                                print(f"Zrekrutowano {unit.name}")
        # ================= TICK =================
        now = pygame.time.get_ticks()
        if not paused and now - last_tick >= TICK_MS:
            last_tick = now
            galaxy.tick()

        # ================= RENDER =================
        screen.fill((0, 0, 0))

        if current_view == GALAXY_VIEW:
            draw_galaxy(
                screen,
                galaxy,
                offset=(LEFT_PANEL_W, 0),
                area=(WIDTH - LEFT_PANEL_W, HEIGHT)
            )

            table_clicks = draw_galaxy_table(screen, galaxy, font)
            
            draw_transport_panel(screen, empire, galaxy, font, pygame.mouse.get_pos())

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
            draw_system(
                screen,
                current_system,
                (LEFT_PANEL_W + (WIDTH - LEFT_PANEL_W)//2, HEIGHT // 2)
            )

            table_clicks = draw_system_table(screen, current_system, font)

            mx, my = pygame.mouse.get_pos()
            for planet, (px,py), orbit in planet_positions:
                if (mx-px)**2 + (my-py)**2 < 8**2:
                    lines = planet_tooltip_data(planet, orbit)
                    y = my + 10
                    for l in lines:
                        screen.blit(font.render(l, True, (220,220,220)), (mx+10, y))
                        y += 16

        elif current_view == PLANET_VIEW:
            visible_height = HEIGHT - 60
            total_height = len(current_planet.hex_map.hexes) * HEX_ROW_H
            max_scroll = max(0, total_height - visible_height)
            
            draw_planet(
                screen,
                current_planet,
                (LEFT_PANEL_W + (WIDTH - LEFT_PANEL_W)//2, HEIGHT // 2),
                selected_hex,
                overlay_mode
            )
            
            build_buttons, header_clicks = draw_planet_hex_table(
                screen,
                current_planet,
                font,
                pygame.mouse.get_pos(),
                hex_table_scroll,
                sort_key
            )

            hover_hex = pick_hex(current_planet, pygame.mouse.get_pos(), 
                                (LEFT_PANEL_W + (WIDTH - LEFT_PANEL_W)//2, HEIGHT // 2))
            if hover_hex:
                lines = hex_tooltip_data(hover_hex, current_planet)
                mx, my = pygame.mouse.get_pos()
                y = my + 10
                for l in lines:
                    screen.blit(font.render(l, True, (230,230,230)), (mx+10, y))
                    y += 16

            # === STORAGE ===
            y = 150
            screen.blit(font.render("STORAGE:", True, (200, 200, 200)), (10+LEFT_PANEL_W, y))
            y += 20
            for res, val in current_planet.storage.items():
                img = font.render(f"{res.upper()}: {val:.1f}", True, (180, 180, 220))
                screen.blit(img, (10 +LEFT_PANEL_W, y))
                y += 18

            # ✅ NOWE - Transport info dla planety
            transports = empire.transport_manager.get_active_transports_for_planet(current_planet)
            if transports:
                y += 10
                screen.blit(
                    font.render(f"TRANSPORTS: {len(transports)} active", True, (200, 220, 240)),
                    (10 + LEFT_PANEL_W, y)
                )

            # === OVERLAY LABELS ===
            labels = ["1 TEMP", "2 HEIGHT", "3 LIFE", "4 RES", "5 PROD", "6 POP"]
            for i, txt in enumerate(labels):
                img = font.render(txt, True, (180, 180, 180))
                screen.blit(img, (10+LEFT_PANEL_W, HEIGHT - 20 * (len(labels) - i)))

            # === BUILD KEYS ===
            build_labels = [
                "B – Build Menu",
                "T – Transport", 
                "M – Recruit Units",  
                "G – View Garrison", 
            ]

            for i, txt in enumerate(build_labels):
                img = font.render(txt, True, (200, 200, 200))
                screen.blit(img, (WIDTH - 160, HEIGHT - 20 * (len(build_labels) - i)))

            # === HEX INFO ===
            if selected_hex:
                res_str = ", ".join(f"{k}:{v:.2f}" for k, v in selected_hex.resources.items())
                lines = [
                    f"TEMP: {selected_hex.temperature:.2f}",
                    f"HEIGHT: {selected_hex.height:.2f}",
                    f"LIFE: {selected_hex.life:.2f}",
                    f"RES: {res_str}",
                ]

                for i, text in enumerate(lines):
                    img = font.render(text, True, (200, 200, 200))
                    screen.blit(img, (10+ LEFT_PANEL_W, 600 + i * 18))
                    
                    if hasattr(current_planet, 'military_manager'):
                        y_military = 750  # lub gdzie masz miejsce
                        military_h = draw_military_panel(
                            screen,
                            current_planet,
                            font,
                            10 + LEFT_PANEL_W,
                            y_military,
                            400
                        )

        # ✅ DODAJ nowe widoki (po istniejących elif):
        elif current_view == MILITARY_RECRUIT_MENU:
            print("mill rec")
            draw_planet(
                screen,
                current_planet,
                (LEFT_PANEL_W + (WIDTH - LEFT_PANEL_W)//2, HEIGHT // 2),
                None,
                overlay_mode
            )
            
            clickable_units = draw_military_production_menu(
                screen,
                current_planet,
                empire,
                font
            )

        elif current_view == MILITARY_GARRISON_VIEW:
            print("mill gar")
            draw_planet(
                screen,
                current_planet,
                (LEFT_PANEL_W + (WIDTH - LEFT_PANEL_W)//2, HEIGHT // 2),
                None,
                overlay_mode
            )
            
            draw_garrison_detail_view(
                screen,
                current_planet,
                font
            )
            draw_military_panel(
                screen,
                current_planet,
                font,
                400,
                400
            )


        elif current_view == BUILD_MENU:
            # Tło planety (opcjonalne)
            draw_planet(
                screen,
                current_planet,
                (LEFT_PANEL_W + (WIDTH - LEFT_PANEL_W)//2, HEIGHT // 2),
                build_menu_hex,
                overlay_mode
            )
            
            # ✅ Nowe scrollowalne menu z kategoriami
            clickable_build_items, clickable_build_tabs = draw_simple_build_menu(
                screen,
                current_planet,
                build_menu_hex,
                build_menu_items,
                font,
                build_menu_state
            )

        elif current_view == SELECT_SOURCE:
            draw_planet(
                screen,
                colonization_target,
                (LEFT_PANEL_W + (WIDTH - LEFT_PANEL_W)//2, HEIGHT // 2),
                build_menu_hex,
                overlay_mode
            )

            draw_source_selection_menu(screen, colonization_sources, galaxy, font)

        # ✅ NOWE - TRANSPORT VIEWS
        elif current_view == TRANSPORT_TARGET_SELECT:
            draw_planet(
                screen,
                transport_source_planet,
                (LEFT_PANEL_W + (WIDTH - LEFT_PANEL_W)//2, HEIGHT // 2),
                None,
                overlay_mode
            )
            
            clickable_planets = draw_transport_creation_menu(
                screen,
                transport_source_planet,
                empire,
                galaxy,
                font
            )

        elif current_view == TRANSPORT_CARGO_SELECT:
            draw_planet(
                screen,
                transport_source_planet,
                (LEFT_PANEL_W + (WIDTH - LEFT_PANEL_W)//2, HEIGHT // 2),
                None,
                overlay_mode
            )
            
            clickable_cargo = draw_cargo_selection_menu(
                screen,
                transport_source_planet,
                transport_target_planet,
                galaxy,
                font
            )

        # === ENERGY PANEL ===
        font_small = pygame.font.SysFont(None, 18)
        font_big = pygame.font.SysFont(None, 24)
        energy_panel_x = 10+LEFT_PANEL_W 
        energy_panel_y = 10
        energy_panel_w = 250
        energy_panel_h = 80
        
        pygame.draw.rect(screen, (20, 25, 35), (energy_panel_x, energy_panel_y, energy_panel_w, energy_panel_h))
        pygame.draw.rect(screen, (60, 80, 100), (energy_panel_x, energy_panel_y, energy_panel_w, energy_panel_h), 2)
        
        screen.blit(
            font_big.render("ENERGY", True, (200, 220, 240)),
            (energy_panel_x + 10, energy_panel_y + 8)
        )
        
        energy_value = empire.energy
        if energy_value >= 50:
            energy_color = (80, 220, 120)
        elif energy_value >= 0:
            energy_color = (220, 200, 80)
        else:
            energy_color = (220, 80, 80)

        screen.blit(
            font_big.render(f"{energy_value:.1f}", True, energy_color),
            (energy_panel_x + 15, energy_panel_y + 32)
        )
        
        delta = empire.energy_last
        delta_text = f"{delta:+.2f}/turn"
        delta_color = (120, 220, 120) if delta >= 0 else (220, 120, 120)

        screen.blit(
            font_small.render(delta_text, True, delta_color),
            (energy_panel_x + 15, energy_panel_y + 56)
        )
        
        arrow = "▲" if delta > 0 else "▼" if delta < 0 else "="
        screen.blit(
            font_big.render(arrow, True, delta_color),
            (energy_panel_x + 110, energy_panel_y + 50)
        )
        
        bar_x = energy_panel_x + 140
        bar_y = energy_panel_y + 35
        bar_w = 90
        bar_h = 12
        
        pygame.draw.rect(screen, (40, 40, 50), (bar_x, bar_y, bar_w, bar_h))
        
        fill_ratio = min(1.0, max(0.0, energy_value / 200.0))
        fill_w = int(bar_w * fill_ratio)
        
        if fill_ratio > 0.5:
            bar_color = (80, 200, 120)
        elif fill_ratio > 0.25:
            bar_color = (220, 180, 80)
        else:
            bar_color = (200, 80, 80)

        pygame.draw.rect(screen, bar_color, (bar_x, bar_y, fill_w, bar_h))
        pygame.draw.rect(screen, (100, 100, 120), (bar_x, bar_y, bar_w, bar_h), 1)
        
        planets_text = f"Planets: {len(empire.planets)}"
        screen.blit(
            font_small.render(planets_text, True, (180, 180, 200)),
            (energy_panel_x + 140, energy_panel_y + 55)
        )
        
        if paused:
            pause_text = font_big.render("PAUSED", True, (220, 80, 80))
            screen.blit(
                pause_text,
                (WIDTH // 2 - pause_text.get_width() // 2, 20)
            )

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


# ============================================
# HELPER FUNCTIONS
# ============================================

from buildings.registry import BUILDINGS

def get_available_buildings(planet, hex):
    """Zwraca listę dostępnych budynków dla danego hexa"""
    from buildings.registry import BUILDINGS
    
    available = []
    
    for name, factory in BUILDINGS.items():
        building = factory()
        
        if hex.can_build(building, planet):
            available.append(building)
    
    return available

def find_valid_source_planets(empire, spaceport):
    valid = []
    for planet in empire.planets:
        if not planet.colonized or planet.population is None:
            continue
        if planet.population.size < 1.0:
            continue

        ok = True
        for res, amount in spaceport.cost.items():
            if planet.storage.get(res, 0.0) < amount:
                ok = False
                break

        if ok:
            valid.append(planet)
    return valid


def draw_source_selection_menu(screen, sources, galaxy, font):
    """Menu wyboru planety źródłowej dla kolonizacji"""
    w, h = screen.get_size()
    x = w // 2 - 200
    y = h // 2 - 250
    
    pygame.draw.rect(screen, (15, 15, 30), (x, y, 400, 480))
    pygame.draw.rect(screen, (120, 120, 180), (x, y, 400, 480), 2)
    
    title = font.render("SELECT SOURCE PLANET", True, (255, 255, 255))
    screen.blit(title, (x + 80, y + 10))
    
    y += 40
    
    if not sources:
        msg = font.render("No valid source planets!", True, (200, 80, 80))
        screen.blit(msg, (x + 80, y + 100))
        return
    
    for i, planet in enumerate(sources):
        py = y + i * 80
        
        pygame.draw.rect(screen, (40, 40, 60), (x + 10, py, 380, 70))
        pygame.draw.rect(screen, (100, 100, 140), (x + 10, py, 380, 70), 1)
        
        num = font.render(f"{i+1}.", True, (220, 220, 220))
        screen.blit(num, (x + 20, py + 10))
        
        system, orbit = planet.get_location(galaxy)
        location = f"System {system.star.type if system else '??'}, Orbit {orbit}"
        loc_text = font.render(location, True, (180, 180, 200))
        screen.blit(loc_text, (x + 50, py + 10))
        
        pop_text = font.render(f"Pop: {planet.population.size:.1f}", True, (200, 200, 200))
        screen.blit(pop_text, (x + 50, py + 28))
        
        energy = planet.storage.get('energy', 0)
        minerals = planet.storage.get('minerals', 0)
        
        res_color = (80, 200, 120) if energy >= 10 and minerals >= 5 else (200, 80, 80)
        res_text = font.render(
            f"Resources: {energy:.0f} energy, {minerals:.0f} minerals",
            True, res_color
        )
        screen.blit(res_text, (x + 50, py + 46))
    
    instruction = font.render("Press 1-9 to select source, ESC to cancel", True, (150, 150, 150))
    screen.blit(instruction, (x + 40, y + len(sources) * 80 + 20))


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        import traceback
        traceback.print_exc()
        input("CRASH – naciśnij ENTER")