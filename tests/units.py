"""
test_minimal_combat_game.py - POPRAWIONA WERSJA
Dłuższe, bardziej epickie bitwy
"""

import pygame
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from galaxy.galaxy import Galaxy
from empire.empire import Empire
from core.init import init_start_planet
from military.units import Infantry, Tank, Fighter
from military.combat import CombatResolver

# ============================================
# CONFIG
# ============================================

WIDTH, HEIGHT = 1600, 900
FPS = 10
TICK_MS = 2000  # 2 sekundy na turę

# Kolory
BG_COLOR = (10, 10, 15)
PANEL_COLOR = (20, 25, 35)
BORDER_COLOR = (60, 70, 90)
TEXT_COLOR = (220, 220, 230)
BUTTON_COLOR = (50, 80, 120)
BUTTON_HOVER = (70, 100, 140)
HEALTH_LOW = (220, 80, 80)
HEALTH_MID = (220, 180, 80)
HEALTH_HIGH = (80, 220, 120)


# ============================================
# MINIMAL GAME
# ============================================

class MinimalCombatGame:
    def __init__(self):
        # Galaktyka
        self.galaxy = Galaxy(system_count=2, size=600)
        self.galaxy.active_invasions = []
        
        # AI empires
        self.empire_a = Empire("Red Empire", (200, 80, 80), self.galaxy, is_player=False)
        self.empire_b = Empire("Blue Empire", (80, 120, 200), self.galaxy, is_player=False)
        
        self.galaxy.empires = [self.empire_a, self.empire_b]
        
        # Init planets
        init_start_planet(self.empire_a, self.galaxy.systems[0])
        init_start_planet(self.empire_b, self.galaxy.systems[1])
        
        # Daj zasoby
        for empire in [self.empire_a, self.empire_b]:
            for planet in empire.planets:
                planet.storage = {
                    "energy": 500, "minerals": 500, "alloys": 200,
                    "organics": 300, "water": 200, "gases": 100,
                    "rare_elements": 100, "electronics": 50, "fuel": 50
                }
                planet.population.size = 20.0
                planet.military_level = 3
                
                # ✅ ZWIĘKSZ LICZBĘ JEDNOSTEK - więcej = dłuższa walka
                self._add_test_units(planet, empire, count=15)  # 15 zamiast 2 - duże bitwy!
        
        # State
        self.paused = True
        self.turn = 0
        self.battle_history = []
        
    def _add_test_units(self, planet, empire, count):
        """Dodaje startowe jednostki - MIX typów dla ciekawszej walki"""
        from military.population_synergy import apply_population_bonuses_to_unit
        
        # Mix: Infantry + Tanks
        for i in range(count):
            if i % 3 == 0:  # Co trzecia jednostka to Tank
                unit = Tank(owner=empire)
            else:
                unit = Infantry(owner=empire)
            
            apply_population_bonuses_to_unit(unit, planet)
            planet.military_manager.garrison.append(unit)
    
    def tick(self):
        """Główna pętla gry"""
        self.turn += 1
        print(f"\n{'='*50}")
        print(f"TURN {self.turn}")
        print(f"{'='*50}")
        
        # Galaxy tick
        self.galaxy.tick()
        
        # ✅ TICK INVASIONS **PRZED** statusem
        finished = []
        for invasion in self.galaxy.active_invasions:
            print(f"[INVASION] Ticking invasion - Status: {invasion.status}, Round: {invasion.resolver.round if invasion.resolver else 0}")

            
            if invasion.status != "in_progress":
                finished.append(invasion)
                self.battle_history.append(invasion)
                print(f"[INVASION] Invasion finished with status: {invasion.status}")
        
        for inv in finished:
            self.galaxy.active_invasions.remove(inv)
        
        # Status
        self.print_status()
    
    def print_status(self):
        """Drukuje status gry"""
        for empire in self.galaxy.empires:
            print(f"\n{empire.name}:")
            for planet in empire.planets:
                garrison = planet.military_manager.garrison
                production = len(planet.military_manager.production_queue.queue)
                print(f"  Planet: {len(garrison)} units, {production} in production")
        
        # Status inwazji
        if self.galaxy.active_invasions:
            print(f"\n[INVASIONS] Active: {len(self.galaxy.active_invasions)}")
            for inv in self.galaxy.active_invasions:
                rounds = inv.resolver.round if inv.resolver else 0
                atk_alive = len([u for u in inv.invasion_force if u.current_health > 0])
                def_alive = len([u for u in inv.target.military_manager.garrison if u.current_health > 0])
                print(f"  Round {rounds}: {atk_alive} attackers vs {def_alive} defenders")


# ============================================
# RENDERING
# ============================================

def draw_panel(screen, x, y, w, h, title, font):
    pygame.draw.rect(screen, PANEL_COLOR, (x, y, w, h))
    pygame.draw.rect(screen, BORDER_COLOR, (x, y, w, h), 2)
    
    if title:
        title_surf = font.render(title, True, TEXT_COLOR)
        screen.blit(title_surf, (x + 10, y + 8))
        return y + 35
    return y + 10

def draw_button(screen, x, y, w, h, text, font, hovered=False):
    color = BUTTON_HOVER if hovered else BUTTON_COLOR
    pygame.draw.rect(screen, color, (x, y, w, h))
    pygame.draw.rect(screen, BORDER_COLOR, (x, y, w, h), 2)
    
    text_surf = font.render(text, True, TEXT_COLOR)
    text_rect = text_surf.get_rect(center=(x + w//2, y + h//2))
    screen.blit(text_surf, text_rect)
    
    return pygame.Rect(x, y, w, h)

def draw_unit_card(screen, x, y, unit, font_small, show_morale=True):
    """Rysuje kartę jednostki z HP, morale, rank"""
    w, h = 200, 90
    
    alive = unit.current_health > 0
    bg = (40, 45, 55) if alive else (30, 20, 20)
    border = (100, 120, 150) if alive else (100, 50, 50)
    
    pygame.draw.rect(screen, bg, (x, y, w, h))
    pygame.draw.rect(screen, border, (x, y, w, h), 2)
    
    # Nazwa + Rank
    name_text = f"{unit.name} [{unit.get_rank()}]"
    name_surf = font_small.render(name_text, True, TEXT_COLOR if alive else (150, 100, 100))
    screen.blit(name_surf, (x + 5, y + 5))
    
    # HP bar
    hp_ratio = max(0, unit.current_health / unit.stats.health)
    bar_w = w - 10
    bar_h = 10
    
    pygame.draw.rect(screen, (40, 40, 50), (x + 5, y + 25, bar_w, bar_h))
    
    if hp_ratio > 0:
        hp_color = HEALTH_HIGH if hp_ratio > 0.6 else HEALTH_MID if hp_ratio > 0.3 else HEALTH_LOW
        pygame.draw.rect(screen, hp_color, (x + 5, y + 25, int(bar_w * hp_ratio), bar_h))
    
    pygame.draw.rect(screen, (100, 100, 120), (x + 5, y + 25, bar_w, bar_h), 1)
    
    # HP text
    hp_text = f"HP: {max(0, unit.current_health):.0f}/{unit.stats.health:.0f}"
    hp_surf = font_small.render(hp_text, True, TEXT_COLOR if alive else (150, 100, 100))
    screen.blit(hp_surf, (x + 5, y + 38))
    
    # Morale bar
    if show_morale:
        morale_ratio = max(0, min(1, unit.current_morale/unit.stats.morale))
        morale_bar_y = y + 52
        
        pygame.draw.rect(screen, (40, 40, 50), (x + 5, morale_bar_y, bar_w, 8))
        
        morale_color = (220, 220, 80) if morale_ratio > 0.5 else (220, 150, 50) if morale_ratio > 0.2 else (220, 80, 80)
        pygame.draw.rect(screen, morale_color, (x + 5, morale_bar_y, int(bar_w * morale_ratio), 8))
        pygame.draw.rect(screen, (100, 100, 120), (x + 5, morale_bar_y, bar_w, 8), 1)
        
        morale_text = f"Morale: {unit.current_morale:.2f}"
        morale_surf = font_small.render(morale_text, True, TEXT_COLOR if alive else (150, 100, 100))
        screen.blit(morale_surf, (x + 5, y + 63))
    
    # Stats
    stats_y = y + 78 if show_morale else y + 52
    atk = font_small.render(f"ATK:{unit.stats.attack:.0f}", True, (220, 150, 150))
    def_t = font_small.render(f"DEF:{unit.stats.defense:.0f}", True, (150, 180, 220))
    xp = font_small.render(f"XP:{unit.experience}", True, (180, 220, 180))
    
    screen.blit(atk, (x + 5, stats_y))
    screen.blit(def_t, (x + 70, stats_y))
    screen.blit(xp, (x + 135, stats_y))
    
    return pygame.Rect(x, y, w, h)

def draw_empire_status(screen, empire, x, y, w, h, font, font_small):
    """Rysuje panel imperium"""
    start_y = draw_panel(screen, x, y, w, h, empire.name, font)
    
    py = start_y
    
    for i, planet in enumerate(empire.planets):
        # Planet header
        system, orbit = planet.get_location(empire.galaxy)
        location = f"Planet {i+1} (Orbit {orbit})"
        
        loc_surf = font_small.render(location, True, (200, 200, 220))
        screen.blit(loc_surf, (x + 10, py))
        py += 18
        
        # Garrison info
        garrison = planet.military_manager.garrison
        production = len(planet.military_manager.production_queue.queue)
        
        garrison_text = f"Garrison: {len(garrison)} units"
        garrison_surf = font_small.render(garrison_text, True, (180, 220, 180))
        screen.blit(garrison_surf, (x + 20, py))
        py += 16
        
        if production > 0:
            prod_text = f"Production: {production} units in queue"
            prod_surf = font_small.render(prod_text, True, (220, 180, 120))
            screen.blit(prod_surf, (x + 20, py))
            py += 16
        
        # Units (max 3 pokazane)
        for j, unit in enumerate(garrison[:3]):
            unit_y = py + j * 95
            draw_unit_card(screen, x + 20, unit_y, unit, font_small, show_morale=True)
        
        if len(garrison) > 3:
            more_text = f"... +{len(garrison)-3} more units"
            more_surf = font_small.render(more_text, True, (150, 150, 170))
            screen.blit(more_surf, (x + 30, py + 3*95))
            py += 3*95 + 18
        else:
            py += len(garrison[:3]) * 95
        
        py += 10

def draw_battle_panel(screen, invasion, x, y, w, h, font, font_small, log_scroll):
    """Rysuje panel aktywnej bitwy"""
    start_y = draw_panel(screen, x, y, w, h, "ACTIVE INVASION", font)
    
    if not invasion:
        no_battle = font_small.render("No active invasion", True, (150, 150, 150))
        screen.blit(no_battle, (x + 10, start_y + 20))
        return
    
    # Status
    if invasion.status == "in_progress":
        status_text = "INVASION IN PROGRESS"
        status_color = (220, 180, 80)
    elif invasion.status == "successful":
        status_text = "INVASION SUCCESSFUL"
        status_color = (80, 220, 120)
    else:
        status_text = "INVASION FAILED"
        status_color = (220, 80, 80)
    
    status_surf = font.render(status_text, True, status_color)
    screen.blit(status_surf, (x + 10, start_y))
    
    # Info
    info_y = start_y + 30
    
    # ✅ Pokazuj LIVE statystyki walki
    rounds = invasion.resolver.round if invasion.resolver else 0
    atk_alive = len([u for u in invasion.invasion_force if u.current_health > 0])
    def_alive = len([u for u in invasion.target.military_manager.garrison if u.current_health > 0])
    
    info = [
        f"Attacker: {invasion.attacker.name}",
        f"Target: Planet owned by {invasion.target.owner.name if invasion.target.owner else 'Neutral'}",
        f"",
        f"Round: {rounds} / 20",
        f"Attackers alive: {atk_alive} / {len(invasion.invasion_force)}",
        f"Defenders alive: {def_alive} / {len(invasion.target.military_manager.garrison)}",
    ]
    
    for line in info:
        surf = font_small.render(line, True, TEXT_COLOR)
        screen.blit(surf, (x + 10, info_y))
        info_y += 16
    
    # Log
    if hasattr(invasion, 'combat_log'):
        log_y = info_y + 20
        log_title = font_small.render("Combat Log:", True, (200, 200, 200))
        screen.blit(log_title, (x + 10, log_y))
        log_y += 20
        
        log_area_h = h - (log_y - y) - 20
        log_surface = pygame.Surface((w - 20, log_area_h))
        log_surface.fill(PANEL_COLOR)
        
        line_height = 14
        visible_lines = invasion.combat_log[-100:]  # Ostatnie 100 linii
        
        for i, line in enumerate(visible_lines):
            line_y = i * line_height - log_scroll
            
            if -line_height < line_y < log_area_h:
                color = TEXT_COLOR
                if "BATTLE START" in line or "BATTLE END" in line:
                    color = (220, 220, 100)
                elif "Round" in line:
                    color = (150, 200, 220)
                elif "destroyed" in line or "DESTROYED" in line:
                    color = (220, 100, 100)
                elif "collapses" in line or "retreats" in line:
                    color = (220, 150, 50)
                
                surf = font_small.render(line[:100], True, color)
                log_surface.blit(surf, (5, line_y))
        
        screen.blit(log_surface, (x + 10, log_y))

def draw_galaxy_view(screen, galaxy, x, y, w, h):
    """Rysuje mini mapę galaktyki"""
    for entry in galaxy.systems:
        sx = entry["x"] * (w / 900) + x
        sy = entry["y"] * (w / 900) + y
        
        # System
        pygame.draw.circle(screen, (100, 120, 150), (int(sx), int(sy)), 8)
        
        # Links
        for link in entry["links"]:
            lx = link["x"] * (w / 900) + x
            ly = link["y"] * (w / 900) + y
            pygame.draw.line(screen, (40, 50, 70), (sx, sy), (lx, ly), 1)
        
        # Planety
        for i, planet in enumerate(entry["system"].planets):
            if planet.owner:
                px = sx + (i - len(entry["system"].planets)//2) * 15
                py = sy - 20
                
                # Planet color
                pygame.draw.circle(screen, planet.owner.color, (int(px), int(py)), 6)
                
                # Garrison size
                garrison = len(planet.military_manager.garrison)
                if garrison > 0:
                    text = str(garrison)
                    surf = pygame.font.SysFont("Arial", 10).render(text, True, (255, 255, 255))
                    screen.blit(surf, (int(px-3), int(py-4)))

# ============================================
# MAIN
# ============================================

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("AI vs AI - Full Combat Simulation")
    clock = pygame.time.Clock()
    
    font = pygame.font.SysFont("Arial", 18, bold=True)
    font_small = pygame.font.SysFont("Arial", 13)
    
    game = MinimalCombatGame()
    
    log_scroll = 0
    
    running = True
    last_auto_tick = pygame.time.get_ticks()
    
    while running:
        mx, my = pygame.mouse.get_pos()
        now = pygame.time.get_ticks()
        
        # Auto-tick
        if not game.paused and now - last_auto_tick >= TICK_MS:
            last_auto_tick = now
            game.tick()
        
        # Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    game.paused = not game.paused
                elif event.key == pygame.K_t:
                    game.tick()
            
            elif event.type == pygame.MOUSEWHEEL:
                if game.galaxy.active_invasions:
                    log_scroll -= event.y * 20
                    log_scroll = max(0, log_scroll)
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Pause button
                pause_btn = pygame.Rect(WIDTH - 150, 10, 140, 40)
                if pause_btn.collidepoint(mx, my):
                    game.paused = not game.paused
                
                # Next turn
                next_btn = pygame.Rect(WIDTH - 150, 60, 140, 40)
                if next_btn.collidepoint(mx, my):
                    game.tick()
        
        # Render
        screen.fill(BG_COLOR)
        
        # Galaxy view
        galaxy_x = 420
        galaxy_y = 20
        galaxy_w = 760
        galaxy_h = 400
        
        draw_panel(screen, galaxy_x, galaxy_y, galaxy_w, galaxy_h, "GALAXY MAP", font)
        draw_galaxy_view(screen, game.galaxy, galaxy_x + 10, galaxy_y + 40, galaxy_w - 20, galaxy_h - 50)
        
        # Empire panels
        draw_empire_status(screen, game.empire_a, 20, 20, 380, HEIGHT - 40, font, font_small)
        draw_empire_status(screen, game.empire_b, WIDTH - 400, 20, 380, HEIGHT - 40, font, font_small)
        
        # Battle panel
        battle_y = galaxy_y + galaxy_h + 20
        battle_h = HEIGHT - battle_y - 20
        
        active_invasion = game.galaxy.active_invasions[0] if game.galaxy.active_invasions else None
        draw_battle_panel(screen, active_invasion, galaxy_x, battle_y, galaxy_w, battle_h, font, font_small, log_scroll)
        
        # Controls
        pause_btn = pygame.Rect(WIDTH - 150, 10, 140, 40)
        pause_hovered = pause_btn.collidepoint(mx, my)
        draw_button(screen, pause_btn.x, pause_btn.y, pause_btn.w, pause_btn.h,
                   "PAUSE" if not game.paused else "RESUME", font_small, hovered=pause_hovered)
        
        next_btn = pygame.Rect(WIDTH - 150, 60, 140, 40)
        next_hovered = next_btn.collidepoint(mx, my)
        draw_button(screen, next_btn.x, next_btn.y, next_btn.w, next_btn.h,
                   "NEXT TURN (T)", font_small, hovered=next_hovered)
        
        # Turn counter
        turn_text = f"Turn: {game.turn}"
        turn_surf = font.render(turn_text, True, TEXT_COLOR)
        screen.blit(turn_surf, (WIDTH - 150, HEIGHT - 40))
        
        # Status
        if game.paused:
            status = font.render("PAUSED - Press SPACE", True, (220, 100, 100))
        else:
            status = font.render("RUNNING", True, (100, 220, 100))
        screen.blit(status, (WIDTH // 2 - 100, HEIGHT - 40))
        
        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.quit()

if __name__ == "__main__":
    main()