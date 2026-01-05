# core/rng.py
import random
from core.config import SEED

_rng = random.Random(SEED)

def rand():
    return _rng.random()

def uniform(a, b):
    return _rng.uniform(a, b)

def choice(seq):
    return _rng.choice(seq)

def randint(a, b):
    return _rng.randint(a, b)

def reseed():
    random.seed()
