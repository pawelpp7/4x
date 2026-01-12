# military/combat.py

import random
from dataclasses import dataclass
from typing import List, Optional

# ============================================
# RESULT
# ============================================

@dataclass
class CombatResult:
    winner: str
    attacker_losses: List
    defender_losses: List
    attacker_damage_dealt: float
    defender_damage_dealt: float
    rounds: int
    log: List[str]

# ============================================
# COMBAT RESOLVER (STATEFUL)
# ============================================

class CombatResolver:
    """
    CombatResolver obsługuje walkę TUROWA:
    - 1 tick = 1 runda
    - przechowuje stan bitwy
    """

    def __init__(self, attackers=None, defenders=None, location=None):
        self.attackers = [u for u in attackers] if attackers else []
        self.defenders = [u for u in defenders] if defenders else []


        self.attacker_losses = []
        self.defender_losses = []

        self.location = location
        self.defender_bonus = 1.15 if location else 1.0

        self.round = 0
        self.max_rounds = 20

        self.finished = False
        self.winner: Optional[str] = None

        self.attacker_damage = 0.0
        self.defender_damage = 0.0

        self.log: List[str] = []

        if attackers and defenders:
            self.log.append("=== BATTLE START ===")
            self.log.append(f"Attackers: {len(self.attackers)}")
            self.log.append(f"Defenders: {len(self.defenders)}")

    # --------------------------------------------
    # PUBLIC API
    # --------------------------------------------

    def tick(self):
        """Jedna runda walki (1 TURA GRY)"""

        if self.finished:
            return

        if not self.attackers or not self.defenders:
            self._finish_battle()
            return

        if self.round >= self.max_rounds:
            self._finish_battle(timeout=True)
            return

        self.round += 1
        self.log.append(f"\n--- Round {self.round} ---")

        all_units = []
        for u in self.attackers:
            all_units.append(("attacker", u))
        for u in self.defenders:
            all_units.append(("defender", u))

        all_units.sort(key=lambda x: x[1].stats.speed, reverse=True)

        for side, unit in all_units:
            if unit.current_health <= 0:
                continue

            enemies = self.defenders if side == "attacker" else self.attackers
            bonus = 1.0 if side == "attacker" else self.defender_bonus

            if not enemies:
                break

            target = self._pick_target(enemies)
            dmg, info = self._calculate_damage_with_breakdown(unit, target, bonus)
            target.current_health = max(0, target.current_health - dmg)
            target.current_morale *=target.current_health/target.stats.health
            target.current_morale-=0.1
            unit.current_morale +=unit.stats.attack/unit.stats.health


            result = self._check_morale(target, "defender" if side == "attacker" else "attacker")

            if result:
                if side == "attacker":
                    self.defender_losses.append({"unit": target, "reason": result})
                    self.defenders.remove(target)
                else:
                    self.attacker_losses.append({"unit": target, "reason": result})
                    self.attackers.remove(target)
                continue
            if side == "attacker":
                self.attacker_damage += dmg
            else:
                self.defender_damage += dmg

            self.log.append(
                f"{unit.name} ({side}) → {target.name} "
                f"{dmg:.1f} dmg (HP {max(0, target.current_health):.1f})"
            )
            self.log.append(
                f"{unit.name} ({side}) attacks {target.name} | "
                f"ATK {info['base_attack']} "
                f"MORALE x{info['morale_atk']:.2f} "
                f"BONUS x{info['bonus']:.2f} "
                f"- ARMOR {info['reduction']:.1f} "
                f"= {info['final']:.1f}"
            )


        for u in self.defenders:
            if u.current_health <= 0:
                self.defender_losses.append(u)

        for u in self.attackers:
            if u.current_health <= 0:
                self.attacker_losses.append(u)

        self.defenders = [u for u in self.defenders if u.current_health > 0]
        self.attackers = [u for u in self.attackers if u.current_health > 0]

                
        if not self.attackers or not self.defenders:
            self._finish_battle()

    # --------------------------------------------
    # FINISH
    # --------------------------------------------

    def _finish_battle(self, timeout=False):
        self.finished = True

        if not self.defenders and self.attackers:
            self.winner = "attacker"
        elif not self.attackers and self.defenders:
            self.winner = "defender"
        else:
            atk_power = sum(u.combat_power() for u in self.attackers)
            def_power = sum(u.combat_power() for u in self.defenders)
            self.winner = "attacker" if atk_power > def_power else "defender"

        self.log.append(f"\n=== BATTLE END: {self.winner.upper()} ===")

    # --------------------------------------------
    # BACKWARD COMPATIBILITY
    # --------------------------------------------

    def resolve_battle(self, attackers, defenders, location=None):
        """STARE API – działa jak dawniej"""
        self.__init__(attackers, defenders, location)

        while not self.finished:
            self.tick()

        return CombatResult(
            winner=self.winner,
            attacker_losses=[u for u in attackers if u.current_health <= 0],
            defender_losses=[u for u in defenders if u.current_health <= 0],
            attacker_damage_dealt=self.attacker_damage,
            defender_damage_dealt=self.defender_damage,
            rounds=self.round,
            log=self.log
        )

    # --------------------------------------------
    # HELPERS
    # --------------------------------------------

    def _pick_target(self, enemies):
        return min(enemies, key=lambda u: u.current_health / u.stats.health)

    def _calculate_damage_with_breakdown(self, attacker, defender, bonus):
        morale_atk = 0.75 + max(attacker.current_morale, 0.25) 
        morale_def = 0.75 + max(defender.current_morale, 0.25) 

        base_attack = attacker.stats.attack
        base = base_attack * morale_atk * bonus
        reduction = defender.stats.defense * 0.3 * morale_def * defender.current_morale

        raw = max(1.0, base - reduction)
        rng = random.uniform(0.8, 1.2)
        final = raw * rng

        return final, {
            "base_attack": base_attack,
            "morale_atk": morale_atk,
            "morale_def": morale_def,
            "bonus": bonus,
            "reduction": reduction,
            "raw": raw,
            "rng": rng,
            "final": final
        }

    def _check_morale(self, unit, side):
        """
        Sprawdza morale jednostki:
        - panic / destruction
        - retreat attempt
        Zwraca True jeśli jednostka ZNIKA z walki
        """

        # TOTAL COLLAPSE
        if unit.current_morale <= 0:
            self.log.append(
                f"{unit.name} ({side}) collapses and is destroyed!"
            )
            return "destroyed"

        # RETREAT ATTEMPT
        if unit.current_morale < 0.25:
            # im niższe morale, tym większa szansa ucieczki
            chance = 0.3 + (0.25 - unit.current_morale) * 2
            if random.random() < chance:
                self.log.append(
                    f"{unit.name} ({side}) breaks morale and retreats!"
                )
                return "retreated"

        return None

# =========================================================
# TICK-BASED COMBAT
# =========================================================

class CombatInstance:
    """Trwająca walka – 1 tick = 1 runda"""

    def __init__(self, attackers, defenders, location=None):
        self.attackers = [u for u in attackers if u.current_health > 0]
        self.defenders = [u for u in defenders if u.current_health > 0]

        self.round = 0
        self.max_rounds = 20
        self.finished = False
        self.winner = None

        self.log = []
        self.defender_bonus = 1.15 if location else 1.0
        self.resolver = CombatResolver()

    def tick(self):
        if self.finished:
            return

        self.round += 1
        self.log.append(f"\n--- ROUND {self.round} ---")

        self.resolver._combat_round(
            self.attackers,
            self.defenders,
            self.defender_bonus,
            self.log
        )

        self.attackers = [u for u in self.attackers if u.current_health > 0]
        self.defenders = [u for u in self.defenders if u.current_health > 0]

        if not self.attackers and not self.defenders:
            self.finished = True
            self.winner = "draw"
        elif not self.defenders:
            self.finished = True
            self.winner = "attacker"
        elif not self.attackers:
            self.finished = True
            self.winner = "defender"
        elif self.round >= self.max_rounds:
            self.finished = True
            self._timeout()

    def _timeout(self):
        atk = sum(u.combat_power() for u in self.attackers)
        deff = sum(u.combat_power() for u in self.defenders)
        self.winner = "attacker" if atk > deff else "defender"

# =========================================================
# BACKWARD COMPATIBILITY
# =========================================================

def resolve_battle(attackers, defenders, location=None):
    """
    STARE API – działa jak wcześniej
    ale wewnętrznie używa ticków
    """

    combat = CombatInstance(attackers, defenders, location)

    while not combat.finished:
        combat.tick()

    return CombatResult(
        winner=combat.winner,
        attacker_losses=[u for u in attackers if u.current_health <= 0],
        defender_losses=[u for u in defenders if u.current_health <= 0],
        attacker_damage_dealt=0,
        defender_damage_dealt=0,
        rounds=combat.round,
        log=combat.log
    )

# =========================================================
# PLANETARY INVASION (TICK SAFE)
# =========================================================

