from buildings import Refinery
from buildings.PopulationHub import PopulationHub
from buildings.SpacePort import SpacePort
from buildings.Mining import MiningComplex
from core.config import ADVANCED_RESOURCES
from military.buildings import MILITARY_BUILDINGS

BUILDINGS = {
    # Infrastructure
    "Population Hub": lambda: PopulationHub(),
    "Space Port":     lambda: SpacePort(),

    # ⛏️ TIER 1: Extractors (Basic Resources)
    "Energy Collector":       lambda: MiningComplex("energy"),
    "Water Extractor":        lambda: MiningComplex("water"),
    "Mining Complex":         lambda: MiningComplex("minerals"),
    "Bio Harvester":          lambda: MiningComplex("organics"),
    "Gas Collector":          lambda: MiningComplex("gases"),
    "Rare Element Extractor": lambda: MiningComplex("rare_elements"),
    
    # 🏭 TIER 2: Refineries (Refined Resources)
    "Smelter":          lambda: Refinery.Smelter(),           # minerals + energy → alloys
    "Chemical Plant":   lambda: Refinery.ChemicalPlant(),     # gases + water + energy → chemicals
    "Bioreactor":       lambda: Refinery.Bioreactor(),        # organics + water → biotech
    "Polymer Factory":  lambda: Refinery.PolymerFactory(),    # organics + chemicals → plastics
    "Electronics Fab":  lambda: Refinery.ElectronicsFab(),    # minerals + rares + energy → electronics
    "Fuel Refinery":    lambda: Refinery.FuelRefinery(),      # organics + chemicals + gases → fuel
    
    **MILITARY_BUILDINGS,
}