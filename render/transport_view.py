"""
render/transport_view.py
UI dla systemu transportu
"""

import pygame

def draw_transport_panel(screen, empire, galaxy, font, mouse_pos):
    """
    Rysuje panel transportów dla imperium
    Pokazuje aktywne transporty i pozwala tworzyć nowe
    """
    if not hasattr(empire, 'transport_manager'):
        return []
        
    x = 20
    y = 300
    w = 520
    h = 400
    
    # Tło panelu
    pygame.draw.rect(screen, (20, 25, 35), (x, y, w, h))
    pygame.draw.rect(screen, (60, 80, 100), (x, y, w, h), 2)
    
    # Nagłówek
    big_font = pygame.font.SysFont(None, 22)
    screen.blit(
        big_font.render("TRANSPORTS", True, (200, 220, 240)),
        (x + 10, y + 8)
    )
    
    ty = y + 35
    
    # Aktywne transporty
    manager = empire.transport_manager
    
    if not manager.transports:
        screen.blit(
            font.render("No active transports", True, (150, 150, 150)),
            (x + 10, ty)
        )
        ty += 20
    else:
        for i, transport in enumerate(manager.transports):
            ty = draw_transport_item(
                screen, transport, galaxy, font,
                x + 10, ty, w - 20
            )
            ty += 5
            
    # Historia (ostatnie dostawy)
    ty += 10
    screen.blit(
        font.render("RECENT DELIVERIES:", True, (180, 180, 200)),
        (x + 10, ty)
    )
    ty += 20
    
    for entry in manager.history[-5:]:  # ostatnie 5
        source_sys, source_orbit = entry["source"].get_location(galaxy)
        target_sys, target_orbit = entry["target"].get_location(galaxy)
        
        if entry["type"] == "resources":
            cargo_str = ", ".join(f"{k}:{v:.0f}" for k, v in entry["cargo"].items())
        else:
            cargo_str = f"Pop: {entry['cargo']:.1f}"
            
        line = f"S{source_orbit}→S{target_orbit}: {cargo_str}"
        color = (100, 200, 100) if entry["status"] == "delivered" else (200, 100, 100)
        
        screen.blit(font.render(line, True, color), (x + 10, ty))
        ty += 16
        
    return []


def draw_transport_item(screen, transport, galaxy, font, x, y, width):
    """Rysuje pojedynczy transport w trakcie podróży"""
    
    # Tło itemu
    pygame.draw.rect(screen, (30, 35, 45), (x, y, width, 70))
    pygame.draw.rect(screen, (80, 90, 110), (x, y, width, 70), 1)
    
    # Lokacje
    source_sys, source_orbit = transport.source.get_location(galaxy)
    target_sys, target_orbit = transport.target.get_location(galaxy)
    
    route = f"System {source_sys.star.type if source_sys else '??'} Orbit {source_orbit}"
    route += f" → System {target_sys.star.type if target_sys else '??'} Orbit {target_orbit}"
    
    screen.blit(font.render(route, True, (200, 200, 220)), (x + 5, y + 5))
    
    # Cargo
    if transport.transport_type == "resources":
        cargo_text = "Resources: " + ", ".join(
            f"{k}:{v:.0f}" for k, v in transport.cargo.items()
        )
    else:
        cargo_text = f"Population: {transport.cargo:.1f}"
        
    screen.blit(font.render(cargo_text, True, (180, 200, 220)), (x + 5, y + 23))
    
    # Progress bar
    progress = transport.progress()
    bar_x = x + 5
    bar_y = y + 45
    bar_w = width - 10
    bar_h = 12
    
    pygame.draw.rect(screen, (40, 40, 50), (bar_x, bar_y, bar_w, bar_h))
    
    fill_w = int(bar_w * progress)
    pygame.draw.rect(screen, (80, 180, 120), (bar_x, bar_y, fill_w, bar_h))
    pygame.draw.rect(screen, (100, 100, 120), (bar_x, bar_y, bar_w, bar_h), 1)
    
    # ETA
    eta_text = f"ETA: {transport.time_remaining} turns"
    screen.blit(font.render(eta_text, True, (150, 150, 170)), (bar_x + bar_w - 100, y + 60))
    
    return y + 75


def draw_transport_creation_menu(screen, source_planet, empire, galaxy, font):
    """
    Menu tworzenia nowego transportu
    Pozwala wybrać planetę docelową i zasoby
    """
    w, h = screen.get_size()
    menu_w = 600
    menu_h = 500
    x = w // 2 - menu_w // 2
    y = h // 2 - menu_h // 2
    
    # Tło
    pygame.draw.rect(screen, (15, 20, 30), (x, y, menu_w, menu_h))
    pygame.draw.rect(screen, (120, 140, 180), (x, y, menu_w, menu_h), 2)
    
    # Tytuł
    big_font = pygame.font.SysFont(None, 26)
    title = big_font.render("CREATE TRANSPORT", True, (255, 255, 255))
    screen.blit(title, (x + menu_w // 2 - title.get_width() // 2, y + 10))
    
    ty = y + 50
    
    # Source info
    source_sys, source_orbit = source_planet.get_location(galaxy)
    source_info = f"FROM: System {source_sys.star.type if source_sys else '??'}, Orbit {source_orbit}"
    screen.blit(font.render(source_info, True, (200, 200, 220)), (x + 20, ty))
    ty += 30
    
    # Lista dostępnych planet docelowych
    screen.blit(
        font.render("SELECT TARGET PLANET:", True, (180, 200, 220)),
        (x + 20, ty)
    )
    ty += 25
    
    clickable_planets = []
    
    for i, planet in enumerate(empire.planets):
        if planet == source_planet:
            continue
            
        target_sys, target_orbit = planet.get_location(galaxy)
        
        py = ty + i * 25
        
        # Prostokąt planety
        rect = pygame.Rect(x + 30, py, menu_w - 60, 22)
        
        # Highlight on hover
        if rect.collidepoint(pygame.mouse.get_pos()):
            pygame.draw.rect(screen, (50, 60, 80), rect)
            
        location = f"{i+1}. System {target_sys.star.type if target_sys else '??'}, Orbit {target_orbit}"
        pop = f"Pop: {planet.population.size:.1f}"
        
        screen.blit(font.render(location, True, (200, 200, 200)), (x + 35, py + 2))
        screen.blit(font.render(pop, True, (150, 150, 150)), (x + 400, py + 2))
        
        clickable_planets.append((planet, rect))
        
    ty += len(empire.planets) * 25 + 20
    
    # Instrukcje
    instructions = [
        "Click planet to select target",
        "ESC to cancel",
    ]
    
    for line in instructions:
        screen.blit(
            font.render(line, True, (120, 120, 140)),
            (x + 20, ty)
        )
        ty += 18
        
    return clickable_planets


def draw_cargo_selection_menu(screen, source_planet, target_planet, galaxy, font):
    """
    Menu wyboru ładunku do wysłania
    """
    w, h = screen.get_size()
    menu_w = 500
    menu_h = 600
    x = w // 2 - menu_w // 2
    y = h // 2 - menu_h // 2
    
    # Tło
    pygame.draw.rect(screen, (15, 20, 30), (x, y, menu_w, menu_h))
    pygame.draw.rect(screen, (120, 140, 180), (x, y, menu_w, menu_h), 2)
    
    # Tytuł
    big_font = pygame.font.SysFont(None, 26)
    title = big_font.render("SELECT CARGO", True, (255, 255, 255))
    screen.blit(title, (x + menu_w // 2 - title.get_width() // 2, y + 10))
    
    ty = y + 50
    
    # Route info
    source_sys, source_orbit = source_planet.get_location(galaxy)
    target_sys, target_orbit = target_planet.get_location(galaxy)
    
    route = f"FROM: Orbit {source_orbit} → TO: Orbit {target_orbit}"
    screen.blit(font.render(route, True, (200, 200, 220)), (x + 20, ty))
    ty += 30
    
    # Dostępne zasoby
    screen.blit(
        font.render("AVAILABLE RESOURCES:", True, (180, 200, 220)),
        (x + 20, ty)
    )
    ty += 25
    
    clickable_resources = []
    
    from core.config import BASIC_RESOURCES
    
    for i, res in enumerate(BASIC_RESOURCES):
        available = source_planet.storage.get(res, 0)
        
        py = ty + i * 25
        rect = pygame.Rect(x + 30, py, menu_w - 60, 22)
        
        if rect.collidepoint(pygame.mouse.get_pos()):
            pygame.draw.rect(screen, (50, 60, 80), rect)
            
        line = f"{i+1}. {res.upper()}: {available:.0f} available"
        color = (200, 200, 200) if available > 10 else (150, 150, 150)
        
        screen.blit(font.render(line, True, color), (x + 35, py + 2))
        
        if available >= 10:
            clickable_resources.append((res, rect))
            
    ty += len(BASIC_RESOURCES) * 25 + 30
    
    # Opcja transferu populacji
    pop_available = source_planet.population.size
    pop_rect = pygame.Rect(x + 30, ty, menu_w - 60, 22)
    
    if pop_rect.collidepoint(pygame.mouse.get_pos()):
        pygame.draw.rect(screen, (50, 60, 80), pop_rect)
        
    pop_line = f"P. POPULATION: {pop_available:.1f} available"
    pop_color = (200, 220, 200) if pop_available > 2.0 else (150, 150, 150)
    screen.blit(font.render(pop_line, True, pop_color), (x + 35, ty + 2))
    
    if pop_available >= 2.0:
        clickable_resources.append(("population", pop_rect))
        
    ty += 40
    
    # Instrukcje
    instructions = [
        "Click resource to send 50 units",
        "Click population to send 2.0 pop",
        "ESC to cancel",
    ]
    
    for line in instructions:
        screen.blit(
            font.render(line, True, (120, 120, 140)),
            (x + 20, ty)
        )
        ty += 18
        
    return clickable_resources