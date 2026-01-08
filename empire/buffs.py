RESOURCE_TO_POP_STAT = {
    "energy":  "energy",
    "gases": "gases",
    "water": "water",
    "minerals":"minerals",
    "organics": "organics",
    "rare_elements": "rare_elements",
}
def population_resource_bonus(population, resource):
    """
    Zwraca mnożnik produkcji na podstawie statów populacji
    """
    stat = RESOURCE_TO_POP_STAT.get(resource)
    if not stat:
        return 1.0

    value = population.stats.get(stat, 0.0)

    # 📐 krzywa wzrostu (bez runaway)
    return 1.0 + (value ** 0.7) * 0.15
