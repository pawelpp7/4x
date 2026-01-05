# render/draw_hex.py
import math
import pygame
from render.colors import RESOURCE_COLORS

HEX_SIZE = 18

def hex_to_pixel(q, r, center_x, center_y):
    x = HEX_SIZE * (math.sqrt(3) * q + math.sqrt(3)/2 * r)
    y = HEX_SIZE * (3/2 * r)
    return int(x + center_x), int(y + center_y)

def hex_corners(x, y):
    corners = []
    for i in range(6):
        angle = math.pi / 180 * (60 * i - 30)
        cx = x + HEX_SIZE * math.cos(angle)
        cy = y + HEX_SIZE * math.sin(angle)
        corners.append((cx, cy))
    return corners

def draw_hex(surface, hex_obj, center_x, center_y, color):
    x, y = hex_to_pixel(hex_obj.q, hex_obj.r, center_x, center_y)
    points = hex_corners(x, y)

    pygame.draw.polygon(surface, color, points)
    pygame.draw.polygon(surface, (20, 20, 20), points, 1)

    if hex_obj.occupied:
        pygame.draw.circle(
            surface,
            (255, 255, 255),
            (x, y),
            5
        )

def point_in_hex(px, py, hex_obj, center_x, center_y):
    x, y = hex_to_pixel(hex_obj.q, hex_obj.r, center_x, center_y)
    corners = hex_corners(x, y)

    inside = False
    j = len(corners) - 1
    for i in range(len(corners)):
        xi, yi = corners[i]
        xj, yj = corners[j]
        intersect = ((yi > py) != (yj > py)) and \
                    (px < (xj - xi) * (py - yi) / (yj - yi + 1e-6) + xi)
        if intersect:
            inside = not inside
        j = i
    
    return inside


def production_hex_color(hex, planet):
    prod = hex.production_summary(planet.population)

    if not prod:
        return (40, 40, 40)

    # wybierz dominujący zasób
    res = max(prod, key=prod.get)
    val = prod[res]

    base = RESOURCE_COLORS.get(res, (120,120,120))

    # jasność zależna od produkcji
    intensity = min(1.0, val / 3.0)

    r = int(base[0] * intensity)
    g = int(base[1] * intensity)
    b = int(base[2] * intensity)

    return (r, g, b)
