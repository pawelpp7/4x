def resolve_battle(attacker_units, defender_units):
    atk_power = sum(u.combat_power() for u in attacker_units)
    def_power = sum(u.combat_power() for u in defender_units)

    print("ATK:", atk_power, "DEF:", def_power)

    if atk_power > def_power:
        winner = "attacker"
        loser_units = defender_units
    else:
        winner = "defender"
        loser_units = attacker_units

    # prosta destrukcja przegranych
    for u in loser_units:
        u.health = 0

    return winner
