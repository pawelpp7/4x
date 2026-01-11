"""
render/military_view.py
Kompletne UI dla systemu wojskowego
"""

import pygame

UNIT_ICONS = {
    "Infantry": "👤",
    "Tank": "🚜",
    "Fighter": "✈️",
    "Frigate": "🚀",
    "Destroyer": "🛸"
}

UNIT_COLORS = {
    "Infantry": (180, 180, 180),
    "Tank": (140, 140, 140),
    "Fighter": (180, 200, 220),
    "Frigate": (120, 180, 220),
    "Destroyer": (100, 150, 200)
}

def draw_military_panel(screen, planet, font, x, y, width=500):
    """Panel wojskowy pokazujący garnizon i produkcję"""
    
    if not hasattr(planet, 'military_manager'):
        return 0
    
    manager = planet.military_manager
    
    panel_height = 400
    pygame.draw.rect(screen, (25, 30, 40), (x, y, width, panel_height))
    pygame.draw.rect(screen, (100, 80, 80), (x, y, width, panel_height), 2)
    
    # Nagłówek
    big_font = pygame.font.SysFont(None, 22)
    title = big_font.render("MILITARY", True, (220, 180, 180))
    screen.blit(title, (x + 10, y + 8))
    
    ty = y + 35
    
    # === GARNIZON ===
    screen.blit(
        font.render("GARRISON:", True, (200, 180, 180)),
        (x + 10, ty)
    )
    ty += 20
    
    if not manager.garrison:
        screen.blit(
            font.render("No units", True, (150, 150, 150)),
            (x + 20, ty)
        )
        ty += 20
    else:
        for unit in manager.garrison[:5]:  # max 5
            ty = draw_unit_compact(screen, unit, font, x + 20, ty, width - 40)
            ty += 2
            
        if len(manager.garrison) > 5:
            more = font.render(
                f"... and {len(manager.garrison) - 5} more",
                True, (150, 150, 150)
            )
            screen.blit(more, (x + 20, ty))
            ty += 18
    
    # Siła
    strength = manager.get_garrison_strength()
    screen.blit(
        font.render(f"Total Strength: {strength:.0f}", True, (220, 200, 180)),
        (x + 10, ty)
    )
    ty += 30
    
    # === KOLEJKA PRODUKCJI ===
    screen.blit(
        font.render("PRODUCTION QUEUE:", True, (200, 180, 180)),
        (x + 10, ty)
    )
    ty += 20
    
    queue = manager.production_queue.queue
    
    if not queue:
        screen.blit(
            font.render("Nothing in production", True, (150, 150, 150)),
            (x + 20, ty)
        )
        ty += 20
    else:
        for i, item in enumerate(queue[:3]):
            ty = draw_production_item(
                screen, item, font, x + 20, ty, width - 40, i == 0
            )
            ty += 5
            
    ty += 10
    
    # === UPKEEP ===
    upkeep = sum(u.stats.upkeep for u in manager.garrison)
    upkeep_text = f"Total Upkeep: {upkeep:.1f} energy/turn"
    upkeep_color = (220, 180, 180) if upkeep < 10 else (220, 120, 120)
    screen.blit(
        font.render(upkeep_text, True, upkeep_color),
        (x + 10, ty)
    )
    
    return panel_height


def draw_unit_compact(screen, unit, font, x, y, width):
    """Kompaktowe wyświetlenie jednostki"""
    
    item_height = 22
    color = UNIT_COLORS.get(unit.name, (150, 150, 150))
    
    # Tło
    pygame.draw.rect(screen, (35, 40, 50), (x, y, width, item_height))
    pygame.draw.rect(screen, color, (x, y, width, item_height), 1)
    
    # Ikona i nazwa
    icon = UNIT_ICONS.get(unit.name, "?")
    text = f"{icon} {unit.name}"
    screen.blit(font.render(text, True, color), (x + 5, y + 4))
    
    # HP bar
    hp_x = x + 150
    hp_y = y + 6
    hp_w = 80
    hp_h = 10
    
    hp_ratio = unit.current_health / unit.stats.health
    
    pygame.draw.rect(screen, (60, 40, 40), (hp_x, hp_y, hp_w, hp_h))
    
    fill_w = int(hp_w * hp_ratio)
    hp_color = (80, 200, 120) if hp_ratio > 0.7 else (220, 180, 80) if hp_ratio > 0.3 else (220, 80, 80)
    pygame.draw.rect(screen, hp_color, (hp_x, hp_y, fill_w, hp_h))
    pygame.draw.rect(screen, (100, 100, 110), (hp_x, hp_y, hp_w, hp_h), 1)
    
    # Ranga
    rank = unit.get_rank()
    screen.blit(
        font.render(rank, True, (180, 180, 200)),
        (hp_x + hp_w + 10, y + 4)
    )
    
    return y + item_height


def draw_production_item(screen, item, font, x, y, width, is_current):
    """Wyświetla element w kolejce produkcji"""
    
    item_height = 35
    unit_name = item["unit_class"].__name__
    color = UNIT_COLORS.get(unit_name, (150, 150, 150))
    
    # Tło
    bg_color = (40, 45, 55) if is_current else (30, 35, 45)
    pygame.draw.rect(screen, bg_color, (x, y, width, item_height))
    pygame.draw.rect(screen, color, (x, y, width, item_height), 2 if is_current else 1)
    
    # Ikona i nazwa
    icon = UNIT_ICONS.get(unit_name, "?")
    text = f"{icon} {unit_name}"
    screen.blit(font.render(text, True, color), (x + 5, y + 4))
    
    # Progress bar (tylko current)
    if is_current:
        progress = item["progress"] / item["time_total"]
        
        bar_x = x + 5
        bar_y = y + 20
        bar_w = width - 10
        bar_h = 10
        
        pygame.draw.rect(screen, (40, 40, 50), (bar_x, bar_y, bar_w, bar_h))
        
        fill_w = int(bar_w * progress)
        pygame.draw.rect(screen, color, (bar_x, bar_y, fill_w, bar_h))
        pygame.draw.rect(screen, (100, 100, 110), (bar_x, bar_y, bar_w, bar_h), 1)
        
        # ETA
        remaining = item["time_total"] - item["progress"]
        eta = f"ETA: {int(remaining)} turns"
        screen.blit(font.render(eta, True, (180, 180, 200)), (bar_x + bar_w - 80, y + 4))
    else:
        time_text = f"{item['time_total']} turns"
        screen.blit(
            font.render(time_text, True, (150, 150, 150)),
            (x + width - 70, y + 10)
        )
    
    return y + item_height


def draw_military_production_menu(screen, planet, empire, font):
    """Menu wyboru jednostki do produkcji"""
    
    from military.units import get_available_units
    
    available = get_available_units(planet)
    
    w, h = screen.get_size()
    menu_w = 600
    menu_h = min(650, 100 + len(available) * 120)
    x = w // 2 - menu_w // 2
    y = h // 2 - menu_h // 2
    
    # Tło
    pygame.draw.rect(screen, (20, 25, 35), (x, y, menu_w, menu_h))
    pygame.draw.rect(screen, (120, 100, 100), (x, y, menu_w, menu_h), 2)
    
    # Tytuł
    big_font = pygame.font.SysFont(None, 26)
    title = big_font.render("RECRUIT UNITS", True, (255, 220, 220))
    screen.blit(title, (x + menu_w // 2 - title.get_width() // 2, y + 10))
    
    ty = y + 50
    
    if not available:
        # Sprawdź poziom Military
        military_level = 0
        if hasattr(planet, 'strategic_manager'):
            military_res = planet.strategic_manager.resources.get('military')
            if military_res:
                military_level = military_res.level
        
        if military_level == 0:
            msg1 = "No Military sources on this planet!"
            msg2 = "Find planets with Toxic sources to recruit units."
            screen.blit(font.render(msg1, True, (200, 150, 150)), (x + 50, ty))
            ty += 20
            screen.blit(font.render(msg2, True, (180, 140, 140)), (x + 50, ty))
        else:
            screen.blit(font.render("No units available", True, (200, 150, 150)), (x + 50, ty))
        
        return []
    
    clickable = []
    
    for i, unit_class in enumerate(available):
        unit = unit_class()
        
        py = ty + i * 120
        
        # Prostokąt jednostki
        rect = pygame.Rect(x + 20, py, menu_w - 40, 110)
        clickable.append((unit_class, rect))
        
        # Hover
        if rect.collidepoint(pygame.mouse.get_pos()):
            pygame.draw.rect(screen, (50, 55, 65), rect)
        
        pygame.draw.rect(screen, UNIT_COLORS.get(unit.name, (150, 150, 150)), rect, 2)
        
        # Numer i ikona
        num_icon = f"{i+1}. {UNIT_ICONS.get(unit.name, '?')} {unit.name}"
        screen.blit(
            big_font.render(num_icon, True, (220, 200, 200)),
            (x + 30, py + 8)
        )
        
        # Statystyki
        stats_y = py + 35
        stats = [
            f"ATK: {unit.stats.attack:.0f}",
            f"DEF: {unit.stats.defense:.0f}",
            f"HP: {unit.stats.health:.0f}",
            f"SPD: {unit.stats.speed}",
            f"⚡ {unit.stats.upkeep}/t"
        ]
        
        sx = x + 30
        for stat in stats:
            screen.blit(font.render(stat, True, (180, 180, 200)), (sx, stats_y))
            sx += 90
        
        # Koszt produkcji
        cost_y = py + 55
        screen.blit(
            font.render("Cost:", True, (200, 180, 180)),
            (x + 30, cost_y)
        )
        
        cx = x + 80
        for res, amount in list(unit.production_cost.items())[:3]:  # max 3
            available_amount = planet.storage.get(res, 0)
            cost_color = (120, 200, 120) if available_amount >= amount else (200, 120, 120)
            
            cost_text = f"{res}: {amount:.0f}"
            screen.blit(font.render(cost_text, True, cost_color), (cx, cost_y))
            cx += 120
        
        # Czas produkcji
        time_text = f"Time: {unit.production_time} turns"
        screen.blit(
            font.render(time_text, True, (180, 180, 200)),
            (x + 30, cost_y + 18)
        )
        
        # Status
        can_afford = all(
            planet.storage.get(res, 0) >= amount 
            for res, amount in unit.production_cost.items()
        )
        
        if can_afford:
            status = "✓ Can recruit"
            status_color = (120, 200, 120)
        else:
            status = "✗ Insufficient resources"
            status_color = (200, 120, 120)
        
        screen.blit(
            font.render(status, True, status_color),
            (x + menu_w - 200, py + 8)
        )
    
    # Instrukcje
    ty = y + menu_h - 35
    instructions = "Click unit to recruit | ESC to cancel"
    screen.blit(
        font.render(instructions, True, (150, 150, 150)),
        (x + 20, ty)
    )
    
    return clickable


def draw_garrison_detail_view(screen, planet, font):
    """Szczegółowy widok garnizonu"""
    
    if not hasattr(planet, 'military_manager'):
        return
    
    manager = planet.military_manager
    
    w, h = screen.get_size()
    panel_w = 700
    panel_h = 600
    x = w // 2 - panel_w // 2
    y = h // 2 - panel_h // 2
    
    # Tło
    pygame.draw.rect(screen, (20, 25, 35), (x, y, panel_w, panel_h))
    pygame.draw.rect(screen, (100, 80, 80), (x, y, panel_w, panel_h), 2)
    
    # Nagłówek
    big_font = pygame.font.SysFont(None, 26)
    title = big_font.render(f"GARRISON ({len(manager.garrison)} units)", True, (255, 220, 220))
    screen.blit(title, (x + 10, y + 10))
    
    ty = y + 50
    
    if not manager.garrison:
        screen.blit(
            font.render("No units in garrison", True, (150, 150, 150)),
            (x + 20, ty)
        )
        return
    
    # Lista jednostek
    for i, unit in enumerate(manager.garrison):
        if ty + 70 > y + panel_h - 50:
            break
            
        ty = draw_unit_detailed(screen, unit, font, x + 20, ty, panel_w - 40)
        ty += 10
    
    # Info na dole
    ty = y + panel_h - 30
    
    strength = manager.get_garrison_strength()
    upkeep = sum(u.stats.upkeep for u in manager.garrison)
    
    info = f"Total: {len(manager.garrison)} units | Strength: {strength:.0f} | Upkeep: {upkeep:.1f} energy/turn"
    screen.blit(font.render(info, True, (200, 180, 180)), (x + 20, ty))


def draw_unit_detailed(screen, unit, font, x, y, width):
    """Szczegółowe wyświetlenie jednostki"""
    
    item_height = 60
    color = UNIT_COLORS.get(unit.name, (150, 150, 150))
    
    # Tło
    pygame.draw.rect(screen, (35, 40, 50), (x, y, width, item_height))
    pygame.draw.rect(screen, color, (x, y, width, item_height), 2)
    
    # Ikona i nazwa
    icon = UNIT_ICONS.get(unit.name, "?")
    text = f"{icon} {unit.name}"
    screen.blit(font.render(text, True, color), (x + 10, y + 5))
    
    # Ranga
    rank = unit.get_rank()
    rank_color = {
        "Recruit": (180, 180, 180),
        "Veteran": (200, 200, 120),
        "Elite": (120, 180, 220),
        "Legendary": (220, 180, 120)
    }.get(rank, (150, 150, 150))
    
    screen.blit(
        font.render(f"[{rank}]", True, rank_color),
        (x + 10, y + 22)
    )
    
    # Statystyki
    stats_x = x + 200
    stats = [
        f"ATK: {unit.stats.attack:.0f}",
        f"DEF: {unit.stats.defense:.0f}",
        f"SPD: {unit.stats.speed}",
    ]
    
    sy = y + 5
    for stat in stats:
        screen.blit(font.render(stat, True, (180, 180, 200)), (stats_x, sy))
        sy += 16
    
    # HP bar
    hp_x = x + 400
    hp_y = y + 10
    hp_w = 150
    hp_h = 14
    
    hp_ratio = unit.current_health / unit.stats.health
    
    pygame.draw.rect(screen, (60, 40, 40), (hp_x, hp_y, hp_w, hp_h))
    
    fill_w = int(hp_w * hp_ratio)
    hp_color = (80, 200, 120) if hp_ratio > 0.7 else (220, 180, 80) if hp_ratio > 0.3 else (220, 80, 80)
    pygame.draw.rect(screen, hp_color, (hp_x, hp_y, fill_w, hp_h))
    pygame.draw.rect(screen, (100, 100, 110), (hp_x, hp_y, hp_w, hp_h), 1)
    
    hp_text = f"{unit.current_health:.0f}/{unit.stats.health:.0f}"
    screen.blit(font.render(hp_text, True, (220, 220, 220)), (hp_x + 5, hp_y + 1))
    
    # XP bar
    xp_y = hp_y + 18
    pygame.draw.rect(screen, (40, 40, 60), (hp_x, xp_y, hp_w, 10))
    
    xp_fill = int(hp_w * (unit.experience / 100))
    pygame.draw.rect(screen, (120, 180, 220), (hp_x, xp_y, xp_fill, 10))
    pygame.draw.rect(screen, (100, 100, 110), (hp_x, xp_y, hp_w, 10), 1)
    
    xp_text = f"XP: {unit.experience:.0f}/100"
    screen.blit(font.render(xp_text, True, (180, 200, 220)), (hp_x + 5, xp_y))
    
    # Combat power
    power = unit.combat_power()
    power_text = f"Power: {power:.0f}"
    screen.blit(font.render(power_text, True, (220, 180, 120)), (hp_x, y + 42))
    
    return y + item_height