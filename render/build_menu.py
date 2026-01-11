"""
render/simple_build_menu.py
Prosty, działający system scrollowania dla build menu
"""

import pygame

class BuildMenuState:
    """Stan menu budowy (używany w main.py)"""
    def __init__(self):
        self.scroll = 0
        self.max_scroll = 0
        self.category_filter = None

# Globalna instancja (będzie w main.py)
# build_menu_state = BuildMenuState()


def draw_simple_build_menu(screen, planet, hex, available_buildings, font, menu_state):
    """
    Proste scrollowalne menu
    
    Args:
        menu_state: BuildMenuState obiekt ze scrollem
    
    Returns:
        clickable_buildings: [(building, rect)]
        clickable_tabs: [(category, rect)]
    """
    w, h = screen.get_size()
    menu_w = 700
    menu_h = 650
    x = w // 2 - menu_w // 2
    y = h // 2 - menu_h // 2
    
    # Tło główne
    pygame.draw.rect(screen, (15, 15, 30), (x, y, menu_w, menu_h))
    pygame.draw.rect(screen, (120, 120, 180), (x, y, menu_w, menu_h), 2)
    
    big_font = pygame.font.SysFont(None, 26)
    
    # === HEADER (nie scrolluje) ===
    header_h = 120
    pygame.draw.rect(screen, (20, 25, 35), (x, y, menu_w, header_h))
    
    title = big_font.render("BUILD MENU", True, (255, 255, 255))
    screen.blit(title, (x + menu_w // 2 - title.get_width() // 2, y + 10))
    
    # Taby kategorii
    tab_y = y + 45
    categories = [
        ("All", None),
        ("Small", "small"),
        ("Major", "major"),
        ("Unique", "planet_unique")
    ]
    
    tab_x = x + 20
    tab_w = 100
    tab_h = 30
    clickable_tabs = []
    
    for cat_name, cat_value in categories:
        tab_rect = pygame.Rect(tab_x, tab_y, tab_w, tab_h)
        
        is_active = (menu_state.category_filter == cat_value)
        is_hovered = tab_rect.collidepoint(pygame.mouse.get_pos())
        
        if is_active:
            bg_color = (60, 80, 120)
        elif is_hovered:
            bg_color = (50, 60, 80)
        else:
            bg_color = (35, 40, 50)
        
        pygame.draw.rect(screen, bg_color, tab_rect)
        pygame.draw.rect(screen, (100, 120, 160), tab_rect, 2 if is_active else 1)
        
        text_color = (220, 220, 240) if is_active else (180, 180, 200)
        text = font.render(cat_name, True, text_color)
        screen.blit(text, (tab_x + tab_w//2 - text.get_width()//2, tab_y + 8))
        
        clickable_tabs.append((cat_value, tab_rect))
        tab_x += tab_w + 10
    
    # Filtruj budynki
    if menu_state.category_filter:
        filtered = [b for b in available_buildings if b.category == menu_state.category_filter]
    else:
        filtered = available_buildings
    
    count_text = f"{len(filtered)} buildings"
    screen.blit(font.render(count_text, True, (180, 180, 200)), (x + 20, tab_y + 40))
    
    # === SCROLLABLE AREA ===
    scroll_y = y + header_h
    scroll_h = menu_h - header_h - 50  # 50 dla footer
    
    # Clip rect
    clip = pygame.Rect(x + 10, scroll_y, menu_w - 20, scroll_h)
    
    if not filtered:
        screen.blit(
            font.render("No buildings available", True, (200, 150, 150)),
            (x + 50, scroll_y + 50)
        )
        return [], clickable_tabs
    
    # Oblicz max scroll
    item_h = 85
    total_h = len(filtered) * item_h
    menu_state.max_scroll = max(0, total_h - scroll_h)
    
    # Clamp scroll
    menu_state.scroll = max(0, min(menu_state.scroll, menu_state.max_scroll))
    
    # Rysuj budynki
    clickable_buildings = []
    
    for i, building in enumerate(filtered):
        item_y = scroll_y + (i * item_h) - menu_state.scroll
        
        # Skip jeśli poza widokiem
        if item_y + item_h < scroll_y or item_y > scroll_y + scroll_h:
            continue
        
        # Rect budynku
        item_rect = pygame.Rect(x + 20, item_y, menu_w - 60, item_h - 5)
        
        # ✅ WAŻNE: Sprawdź czy rect jest w widocznym obszarze
        visible_rect = item_rect.clip(clip)
        if visible_rect.width == 0 or visible_rect.height == 0:
            continue
        
        # Hover (tylko jeśli w widocznym obszarze)
        mx, my = pygame.mouse.get_pos()
        is_hovered = visible_rect.collidepoint(mx, my)
        
        if is_hovered:
            pygame.draw.rect(screen, (50, 55, 65), item_rect)
        
        # Tło
        pygame.draw.rect(screen, (35, 40, 50), item_rect)
        pygame.draw.rect(screen, (100, 120, 160), item_rect, 2 if is_hovered else 1)
        
        # Nazwa
        name = big_font.render(building.name, True, (220, 220, 240))
        screen.blit(name, (item_rect.x + 10, item_rect.y + 8))
        
        # Kategoria
        cat = font.render(f"[{building.category}]", True, (140, 140, 160))
        screen.blit(cat, (item_rect.x + 10, item_rect.y + 32))
        
        # Koszt
        cost_x = item_rect.x + 300
        cost_y = item_rect.y + 12
        for res, amount in list(building.cost.items())[:3]:
            avail = planet.storage.get(res, 0)
            color = (120, 200, 120) if avail >= amount else (200, 120, 120)
            
            text = f"{res[:3]}: {amount:.0f}"
            screen.blit(font.render(text, True, color), (cost_x, cost_y))
            cost_x += 85
        
        # Upkeep
        upkeep = f"Up: {building.pop_upkeep:.1f}p {building.energy:.1f}e"
        screen.blit(font.render(upkeep, True, (130, 130, 150)), (item_rect.x + 300, item_rect.y + 30))
        
        # Status
        can_afford = building.can_afford(planet)
        status = "✓" if can_afford else "✗"
        color = (120, 200, 120) if can_afford else (200, 120, 120)
        screen.blit(big_font.render(status, True, color), (item_rect.x + menu_w - 100, item_rect.y + 15))
        
        # ✅ Dodaj do clickable TYLKO widoczny rect
        clickable_buildings.append((building, visible_rect))
    
    # === SCROLLBAR ===
    if menu_state.max_scroll > 0:
        bar_x = x + menu_w - 20
        bar_w = 12
        bar_h = scroll_h
        
        # Track
        pygame.draw.rect(screen, (30, 30, 40), (bar_x, scroll_y, bar_w, bar_h))
        
        # Thumb
        thumb_ratio = scroll_h / total_h
        thumb_h = max(30, int(bar_h * thumb_ratio))
        
        scroll_ratio = menu_state.scroll / menu_state.max_scroll
        thumb_y = scroll_y + int((bar_h - thumb_h) * scroll_ratio)
        
        pygame.draw.rect(screen, (100, 120, 160), (bar_x, thumb_y, bar_w, thumb_h))
        pygame.draw.rect(screen, (120, 140, 180), (bar_x, thumb_y, bar_w, thumb_h), 1)
    
    # === FOOTER (nie scrolluje) ===
    footer_y = y + menu_h - 45
    pygame.draw.rect(screen, (20, 25, 35), (x, footer_y, menu_w, 45))
    pygame.draw.line(screen, (100, 100, 120), (x, footer_y), (x + menu_w, footer_y), 1)
    
    inst = "Click to build | Mouse wheel to scroll | ESC to cancel"
    screen.blit(font.render(inst, True, (150, 150, 150)), (x + 20, footer_y + 12))
    
    return clickable_buildings, clickable_tabs


def handle_build_menu_scroll(menu_state, scroll_delta):
    """
    Obsługa scrollowania
    
    Args:
        menu_state: BuildMenuState
        scroll_delta: Wartość z event.y (np. 1 lub -1)
    """
    menu_state.scroll -= scroll_delta * 50  # 50px per tick
    menu_state.scroll = max(0, min(menu_state.scroll, menu_state.max_scroll))