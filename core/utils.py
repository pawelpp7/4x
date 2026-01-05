# core/utils.py

def clamp(value, min_v, max_v):
    return max(min_v, min(value, max_v))

def hex_distance(a, b):
    # axial coords (q, r)
    return (abs(a.q - b.q)
          + abs(a.q + a.r - b.q - b.r)
          + abs(a.r - b.r)) // 2
