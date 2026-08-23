import random
import sys

sys.path.insert(0, ".")
sys.path.insert(0, "tools")

from playthrough import install_quiet_ui, run_event_with_script
from src.entities.unit import Player
from src.systems.kingdom import Kingdom
from src.systems import naming as naming_sys
from src.systems import events as events_sys

install_quiet_ui()
rng = random.Random(2026)
hero = Player("DbgWar", "slime")
state = {"hero": hero,
         "world": {"zone": "jura_plains", "floor": 1, "day": 20, "phase": 1,
                   "flags": {"village_founded": True}, "bosses_slain": [],
                   "unlocked_zones": [], "recruit_pool": None},
         "roster": [], "captures": [],
         "kingdom": Kingdom()}

fights = 0
while hero.level < 17 and fights < 250:
    mid = rng.choice(["dire_wolf", "orc_soldier", "giant_ant", "horned_rabbit"])
    from tools.autotest import auto_battle as _ab, silent_devour
    b = _ab(hero, [], [mid], seed=rng.randint(0, 10**6))
    fights += 1
    if b.result == "win":
        for _ in hero.gain_xp(sum(e.xp_reward for e in b.enemies)):
            hero.level_up(); hero.check_evolution()
        silent_devour({"hero": hero}, b.enemies)
    hero.hp = hero.max_hp; hero.mp = hero.max_mp
print("grind done:", fights, "fights, Lv", hero.level, flush=True)

wolf = naming_sys.Subordinate("Fang", "dire_wolf", level=15)
wolf.apply_named_form()
wolf.assignment = "party"
state["roster"].append(wolf.to_dict())

flags = state["world"]["flags"]
flags["orc_war_warned"] = True
flags["orc_war_countdown"] = 0

scripted = type("S", (), {"answers": ["field"] * 5})()
import src.core.ui as _uicheck
print("pre-event choose is wrapper:", _uicheck.choose.__name__ if callable(_uicheck.choose) else "?", flush=True)
run_event_with_script(events_sys.orc_war_event, state, scripted)
print("post-event choose:", _uicheck.choose.__name__, flush=True)

print("hero skills at end:", sorted(hero.skills.keys()))
print("WAR DONE:", flags.get("orc_war_done"), "| souls:", hero.souls)
