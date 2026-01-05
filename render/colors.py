# render/colors.py
import math

def clamp01(v):
    return max(0.0, min(1.0, v))

def normalize(v, scale=2.0):
    return clamp01((v + scale) / (2 * scale))

def lerp(a, b, t):
    return a + (b - a) * t

def lerp_color(c1, c2, t):
    return (
        int(lerp(c1[0], c2[0], t)),
        int(lerp(c1[1], c2[1], t)),
        int(lerp(c1[2], c2[2], t)),
    )

TEMP_COLD = (60, 140, 255)
TEMP_NEUTRAL = (130, 130, 130)
TEMP_HOT = (255, 90, 40)

HEIGHT_LOW = (20, 40, 120)      # ocean
HEIGHT_NEUTRAL = (120, 120, 120)
HEIGHT_HIGH = (200, 200, 200)

LIFE_LOW = (110, 80, 60)
LIFE_NEUTRAL = (120, 120, 120)
LIFE_HIGH = (40, 180, 70)

def blend_param(v, low, mid, high):
    v = max(-2.0, min(2.0, v))

    if v < 0:
        t = normalize(v)
        return lerp_color(low, mid, t)
    else:
        t = normalize(v)
        return lerp_color(mid, high, t)

def color_from_params(temp, height, life):
    # 1️⃣ BAZA: terrain (height)
    base = blend_param(height, HEIGHT_LOW, HEIGHT_NEUTRAL, HEIGHT_HIGH)

    # 2️⃣ TINT: temperatura
    tint = blend_param(temp, TEMP_COLD, (255, 255, 255), TEMP_HOT)

    # 3️⃣ LIFE = wzmacnia zieleń
    life_factor = clamp01((life + 1.0) / 2.0)

    # miks bazowy + tint
    r = int(base[0] * 0.7 + tint[0] * 0.3)
    g = int(base[1] * 0.7 + tint[1] * 0.3)
    b = int(base[2] * 0.7 + tint[2] * 0.3)

    # dodanie życia (zieleni)
    g = min(255, int(g + life_factor * 80))

    return (r, g, b)



STAR_COLORS = {
    "red_dwarf": (200, 80, 80),
    "yellow": (220, 220, 120),
    "blue_giant": (120, 160, 255),
}

BACKGROUND = (10, 10, 15)


RESOURCE_COLORS = {
    "thermal":   (200, 80, 60),
    "cryo":      (120, 180, 255),
    "solids":    (160, 140, 110),
    "fluidics":  (80, 140, 200),
    "biomass":   (80, 180, 100),
    "compounds": (180, 160, 220),
}
