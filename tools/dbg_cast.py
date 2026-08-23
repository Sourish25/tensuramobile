import sys
import random
sys.path.insert(0, ".")
sys.path.insert(0, "tools")
from src.entities.unit import Player, enemy_from_template
from src.systems import combat
from src.data.skills import get_skill

hero = Player("Dbg", "slime")
hero.level = 17
for _ in range(16):
    hero.gain_xp(hero.xp_to_next())
    hero.level_up()
    hero.check_evolution()
print("has icicle:", hero.has_skill("icicle_lance"), "| MP:", hero.mp)

enemy = enemy_from_template("orc_lord_geld", 1.0)
b = combat.Battle(hero, [], [enemy], location="dbg")

calls = []
def recorder(prompt, options, allow_cancel=False, cancel_label="Back"):
    calls.append((prompt[:30], len(options)))
    low = prompt.lower()
    if "turn - command" in low:
        return options.index("Skill") if "Skill" in options else 1
    if "use which skill" in low:
        for n, o in enumerate(options):
            if "icicle" in o.lower():
                return n
        return 0
    if "target" in low:
        return 0
    return 0

import src.core.ui as ui
ui.choose = recorder

rng = random.Random(1)
b.rng = rng
rounds = 0
while b.result is None and rounds < 70:
    order = sorted(b.party + b.foes, key=lambda u: -u.eff_stat("agi"))
    for u in order:
        if b.result or not u.alive:
            continue
        b.start_of_turn(u)
        if not u.alive or u.is_acting_blocked():
            continue
        if u is hero:
            b.player_turn(u)
        else:
            b.enemy_turn(u)
    if b.result is None:
        for e in b.enemies:
            if e.alive:
                b.apply_regen(e); e.tick_statuses(); b.check_phases(e)
        hero.tick_statuses()
        b.check_end()
        rounds += 1

print("result:", b.result, "geld hp:", enemy.hp, "/", enemy.max_hp, "rounds:", rounds)
print("menu calls:", len(calls))
for c in calls[:8]:
    print("  ", c)
