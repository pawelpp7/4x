from buildings.PopulationHub import PopulationHub
from buildings.SpacePort import SpacePort
from buildings.Mining import MiningComplex

BUILDINGS = {
    "Population Hub": lambda: PopulationHub(),
    "Space Port":     lambda: SpacePort(),

    # Kopalnie - nazwy zgodne z resource
    "Thermal Mine":   lambda: MiningComplex("thermal"),
    "Cryo Mine":      lambda: MiningComplex("cryo"),
    "Solids Mine":    lambda: MiningComplex("solids"),
    "Fluidics Mine":  lambda: MiningComplex("fluidics"),
    "Biomass Mine":   lambda: MiningComplex("biomass"),
    "Compounds Mine": lambda: MiningComplex("compounds"),
}
