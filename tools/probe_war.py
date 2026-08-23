import sys
sys.path.insert(0, ".")
sys.path.insert(0, "tools")
from playthrough import install_quiet_ui
install_quiet_ui()
import src.core.ui as ui
from src.entities.unit import Player
from src.systems import events as events_sys
from src.systems import naming as naming_sys
from src.systems.kingdom import Kingdom

calls = {"n": 0}
_orig_choose = ui.choose

def probe(prompt, options, allow_cancel=False, cancel_label="Back"):
    calls["n"] += 1
    r = _orig_choose(prompt, options, allow_cancel, cancel_label)
    if calls["n"] <= 25:
        auto_state = getattr(state["hero"], "auto", "??")
        print(f"CHOOSE{calls['n']:03d} {prompt[:34]!r} n={len(options)} -> {r} "
              f"| hero.auto={auto_state} hp={state['hero'].hp}", file=sys.stderr, flush=True)
    if calls["n"] > 60:
        import faulthandler
        faulthandler.dump_traceback()
        sys.exit(77)
    return r

ui.choose = probe

hero = Player("Probe", "slime")
state = {"hero": hero,
         "world": {"zone": "x", "floor": 1, "day": 20, "phase": 1,
                   "flags": {"village_founded": True}, "bosses_slain": [],
                   "unlocked_zones": [], "recruit_pool": None},
         "roster": [], "captures": [], "kingdom": Kingdom()}
w = naming_sys.Subordinate("Fang", "dire_wolf", level=15)
w.apply_named_form()
w.assignment = "party"
state["roster"].append(w.to_dict())
state["world"]["flags"]["orc_war_warned"] = True
state["world"]["flags"]["orc_war_countdown"] = 0

events_sys.orc_war_event(state)
print("survived; war_done =", state["world"]["flags"].get("orc_war_done"))
