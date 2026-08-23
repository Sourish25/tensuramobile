import sys
import types

sys.path.insert(0, ".")

from src.core import ui


class ScriptedUI:
    def __init__(self):
        self.queue = []
        self.log = []

    def push(self, *vals):
        self.queue.extend(vals)

    def next_of_type(self, want_type, context=""):
        self.log.append(context)
        for i, v in enumerate(self.queue):
            if isinstance(v, want_type) and not isinstance(v, bool):
                return self.queue.pop(i)
        raise RuntimeError(f"Script ran dry ({want_type.__name__}) at: {context}")

    def next_menu_token(self, context=""):
        self.log.append(context)
        for i, v in enumerate(self.queue):
            if isinstance(v, tuple) and len(v) == 2 and v[0] == "pick":
                return self.queue.pop(i)
            if isinstance(v, int) and not isinstance(v, bool):
                return self.queue.pop(i)
        raise RuntimeError(f"Script ran dry (menu token) at: {context}")

    def next(self, context=""):
        return self.queue.pop(0)


SCRIPT = ScriptedUI()


def fake_menu(prompt, options, allow_cancel=False, cancel_label="Back", color=None):
    print(f"[MENU] {prompt}")
    for i, o in enumerate(options, 1):
        print(f"   {i}. {o[:70]}")
    while True:
        raw = SCRIPT.next_menu_token(prompt)
        if isinstance(raw, tuple) and raw and raw[0] == "pick":
            needle = raw[1].lower()
            hit = next((n for n, o in enumerate(options, 1) if needle in o.lower()), None)
            print(f"   -> pick '{needle}' => {hit}")
            if hit:
                return hit
            continue
        print(f"   -> {raw}")
        if allow_cancel and raw == 0:
            return None
        if 1 <= raw <= len(options):
            return raw


def fake_pause(msg=""):
    pass


def fake_input(prompt=""):
    v = SCRIPT.next_of_type(str, f"INPUT {prompt}")
    print(f"[INPUT] -> {v}")
    return v


def install():
    ui.menu = fake_menu
    ui.pause = fake_pause
    import builtins
    builtins.input = fake_input


def run_village_flow():
    from src.entities.unit import Player
    from src.systems import naming as naming_sys
    from src.screens import hub

    hero = Player("VillHero", "slime")
    for _ in range(10):
        hero.gain_xp(hero.xp_to_next())
        hero.level_up()
        hero.check_evolution()
    hero.hp = hero.max_hp
    hero.mp = hero.max_mp
    state = {
        "hero": hero,
        "world": {"zone": "goblin_village", "floor": 1, "day": 5, "phase": 1,
                  "flags": {}, "bosses_slain": [], "unlocked_zones": [], "recruit_pool": None},
        "roster": [],
        "captures": [],
        "kingdom": None,
    }

    SCRIPT.push(
        1,
        1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
        "Rigurd",
    )
    hub.first_meeting(state)

    flags = state["world"]["flags"]
    assert flags.get("village_met") is True, "village_met flag not set"
    assert flags.get("village_founded") is True, "village_founded flag not set"
    roster = naming_sys.load_roster(state)
    assert any(s.name == "Rigurd" for s in roster), f"Rigurd missing: {[s.name for s in roster]}"
    rig = next(s for s in roster if s.name == "Rigurd")
    assert rig.evolve_name == "Hobgoblin", f"Rigurd should be Hobgoblin, got {rig.evolve_name}"
    assert rig.assignment == "party", "Rigurd should be in party"
    assert hero.mp_scar > 0, "naming cost not paid"

    pool = state["world"].get("recruit_pool")
    assert isinstance(pool, list) and len(pool) >= 2, "recruit pool not generated"
    print()
    print("VILLAGE FLOW OK -", ", ".join(f"{s.name}({s.evolve_name or s.species})" for s in roster))
    return state


def run_capture_naming():
    from src.entities.unit import Player
    from src.systems import naming as naming_sys

    hero = Player("Capturer", "slime")
    state = {"hero": hero, "world": {"day": 1}, "roster": [], "captures": []}
    naming_sys.captures_add(state, "dire_wolf", 3)
    SCRIPT.push(1, 1, "Fang", 1, 0)
    naming_sys.captures_menu(state)
    assert not state["captures"], "capture not consumed"
    roster = naming_sys.load_roster(state)
    assert any(s.name == "Fang" and s.evolve_name == "Tempest Wolf" for s in roster)
    print("CAPTURE NAMING OK - Fang is a Tempest Wolf")


def run_party_battle_with_sub():
    from src.entities.unit import Player, Subordinate
    from tools.autotest import auto_battle

    results = []
    for seed in range(6):
        hero = Player("Leader", "slime")
        sub = Subordinate("Ranga", "dire_wolf", level=5)
        b = auto_battle(hero, [sub], ["horned_rabbit", "horned_rabbit"], seed=seed)
        assert b.result == "win", f"party battle failed vs rabbits seed {seed}"
        results.append(b.round_no)
    print(f"PARTY BATTLE OK - wins 6/6, rounds {results}")


def run_kingdom_governance():
    from src.entities.unit import Player
    from src.systems.kingdom import Kingdom
    from src.screens import kingdom as kscreen

    hero = Player("Governor", "slime")
    hero.materials.update({"timber": 10, "stone": 5, "spider_silk": 3, "magic_crystal_shard": 6})
    state = {"hero": hero, "world": {"day": 2}, "kingdom": Kingdom(), "roster": [], "captures": []}
    k = state["kingdom"]

    SCRIPT.push(
        1,
        ("pick", "Farm Plots"),
        0,
        3,
        1,
        ("pick", "20%"),
        3,
        7,
        8,
    )
    kscreen.kingdom_menu(state)

    fp = k.buildings["farm_plots"]
    assert fp["days_left"] > 0, f"farm_plots construction not started: {fp}"
    assert k.treasury == 250 - 200, f"build cost not deducted: {k.treasury}"
    assert k.tax_idx == 2, "tax not set"
    print(f"GOVERNANCE OK - {bdata_name('farm_plots')} underway ({fp['days_left']}d), tax {k.tax_rate}%, treasury {k.treasury}g")


def bdata_name(bid):
    from src.data.buildings import BUILDINGS
    return BUILDINGS[bid]["name"]


def run_daily_tick_and_siege_setup():
    from src.entities.unit import Player
    from src.systems.kingdom import Kingdom

    hero = Player("Ticked", "slime")
    k = Kingdom()
    k.buildings["schoolhouse"]["done"] = True
    for _ in range(5):
        evs = k.daily_tick(hero, 1)
    assert k.rp > 0, "research not flowing with schoolhouse"
    assert k.total_pop >= 120, "population not growing"

    k.relations["church"] = -40
    k.pending_siege = {"faction": "church", "days": 1}
    evs = k.daily_tick(hero, 1)
    assert any(e[0] == "siege" and e[1] == "church" for e in evs), f"siege not firing: {evs}"
    print(f"TICK OK - RP {k.rp:.0f}, pop {k.total_pop}, siege fired on schedule")


if __name__ == "__main__":
    install()
    run_party_battle_with_sub()
    run_capture_naming()
    run_kingdom_governance()
    run_daily_tick_and_siege_setup()
    run_village_flow()
    print()
    print("E2E ALL PASSED")
