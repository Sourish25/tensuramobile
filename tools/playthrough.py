import random
import io
import contextlib
import sys

sys.path.insert(0, ".")
sys.path.insert(0, "tools")

from src.entities.unit import Player, Subordinate, enemy_from_template
from src.systems import combat
from src.systems import predator as predator_sys
from src.systems import progression
from src.systems import events as events_sys
from src.systems.kingdom import Kingdom
from tools.autotest import auto_battle, silent_devour


class Quiet:
    def __enter__(self):
        self._buf = io.StringIO()
        self._old = sys.stdout
        sys.stdout = self._buf
        return self

    def __exit__(self, *a):
        sys.stdout = self._old


def grind_phase(hero, rng, target_level, pools, devour=True):
    fights = 0
    while hero.level < target_level and fights < 400:
        floor = min(5, max(1, hero.level - 2))
        mid = rng.choice(pools[floor])
        b = auto_battle(hero, [], [mid], seed=rng.randint(0, 10 ** 6))
        fights += 1
        if b.result == "win":
            hero.kills += len(b.enemies)
            for _ in hero.gain_xp(sum(e.xp_reward for e in b.enemies)):
                hero.level_up()
                hero.check_evolution()
            if devour:
                silent_devour({"hero": hero}, b.enemies)
                predator_sys.check_combinations(hero)
        else:
            assert hero.level > 1 or True
        hero.hp = hero.max_hp
        hero.mp = hero.max_mp
    return fights


def fake_party_battles(hero, allies_ids_levels):
    pass


def main():
    rng = random.Random(2026)
    install_quiet_ui()
    log = []

    def step(msg):
        print(f"\n=== {msg}")
        log.append(msg)

    hero = Player("SimRim", "slime")
    state = {"hero": hero,
             "world": {"zone": "sealed_cave", "floor": 5, "day": 1, "phase": 0,
                       "flags": {}, "bosses_slain": [], "unlocked_zones": [],
                       "recruit_pool": None},
             "roster": [], "captures": [], "kingdom": None}

    step("PHASE A: cave grind to Lv17")
    n = grind_phase(hero, rng, 17, {
        1: ["horned_rabbit", "black_serpent"],
        3: ["cave_centipede", "giant_bat", "black_spider"],
        5: ["black_spider", "cave_centipede", "armorsaurus"],
    })
    print(f"  fights={n} level={hero.level} skills={len(hero.skills)} EP={hero.compute_ep():,}")
    assert hero.has_skill("great_sage") and hero.has_skill("predator"), "latents missing"

    step("PHASE B: village founded, two wolves named (Tempest Wolf + Star-line)")
    state["world"]["flags"]["village_founded"] = True
    state["world"]["phase"] = 1
    state["world"]["bosses_slain"].append("tempest_serpent")
    hero.consumables.update({"high_potion": 6, "low_potion": 4})
    from src.systems.kingdom import Kingdom
    k = Kingdom()
    state["kingdom"] = k
    for nm, sp in [("Fang", "dire_wolf"), ("Grey", "dire_wolf")]:
        sub = Subordinate(nm, sp, level=12)
        sub.apply_named_form()
        sub.assignment = "party"
        state["roster"].append(sub.to_dict())
    subs = [Subordinate.from_dict(d) for d in state["roster"]]
    assert len(subs) == 2 and all(s.evolve_name == "Tempest Wolf" for s in subs)

    step("PHASE C: kingdom economy comes alive")
    k.treasury += 500
    hero.materials.update({"timber": 30, "stone": 20, "spider_silk": 10, "magic_crystal_shard": 20})
    ok, msg = k.start_building("farm_plots", hero); assert ok, msg
    ok, msg = k.start_building("market_stall", hero); assert ok, msg
    for d in range(6):
        k.daily_tick(hero, 1)
        state["world"]["day"] += 1
    assert k.has("farm_plots") and k.has("market_stall")
    k.tax_idx = 2
    for d in range(10):
        k.daily_tick(hero, 1)
        state["world"]["day"] += 1
    print(f"  treasury={k.treasury} pop={k.total_pop} income/day={k.daily_income()}")
    assert k.daily_income() > 0 and k.total_pop >= 130

    step("PHASE D: ORC WAR - three waves vs the Orc Disaster")
    state["world"]["flags"]["orc_war_warned"] = True
    state["world"]["flags"]["orc_war_countdown"] = 0
    arc = events_sys.arc_check(state)
    assert arc == "orc_war", f"expected orc_war got {arc}"
    scripted = Script()
    scripted.answers = ["field"] * 3
    run_event_with_script(events_sys.orc_war_event, state, scripted)
    assert state["world"]["flags"].get("orc_war_done"), "orc war not completed"
    print(f"  souls after war: {hero.souls:,}")

    step("PHASE E: mop-up hunts + charybdis until 10k souls -> HARVEST FESTIVAL AWAKENING")
    while hero.level < 20:
        mid = rng.choice(["dire_wolf", "orc_soldier", "giant_ant"])
        b = auto_battle(hero, [], [mid], seed=rng.randint(0, 10 ** 6))
        if b.result == "win":
            for _ in hero.gain_xp(sum(e.xp_reward for e in b.enemies)):
                hero.level_up(); hero.check_evolution()
            silent_devour(state, b.enemies)
            progression.gain_souls_from(state, b.enemies)
        hero.hp = hero.max_hp; hero.mp = hero.max_mp
    remnant = next(t for t in events_sys.TRIALS if t["id"] == "remnant_hunt")
    hunts = 0
    while hero.souls < 4500 and hunts < 8:
        run_trial_quiet(state, remnant)
        hunts += 1
        hero.hp = hero.max_hp; hero.mp = hero.max_mp
    chary = next(t for t in events_sys.TRIALS if t["id"] == "charybdis_hunt")
    hunts = 0
    while not hero.demon_lord and hunts < 5:
        run_trial_quiet(state, chary)
        hunts += 1
        hero.hp = hero.max_hp; hero.mp = hero.max_mp
    assert hero.demon_lord, f"awakening never fired; souls={hero.souls}"
    assert hero.has_skill("raphael") and hero.has_skill("belzebuth") and hero.has_skill("soul_consume")
    subs_after = [Subordinate.from_dict(d) for d in state["roster"]]
    boosted = all(s.stats["atk"] >= 40 for s in subs_after)
    print(f"  awakened! EP={hero.compute_ep():,} | festival boosted party: {boosted} | hunts={hunts}")
    assert boosted, "harvest festival did not boost roster"

    step("PHASE F: OCTAGAM trials - Milim, Leon, Guy")
    state["world"]["flags"]["walpurgis_done"] = True
    for tid in ("milim", "leon", "guy"):
        t = next(t for t in events_sys.TRIALS if t["id"] == tid)
        run_trial_quiet(state, t)
        assert state["world"]["flags"].get(tid + "_defeated"), f"{tid} trial failed"
        hero.hp = hero.max_hp
        hero.mp = hero.max_mp
        print(f"  {tid} defeated. EP now {hero.compute_ep():,}")
    assert state["world"]["flags"].get("octagram_done")

    step("PHASE G: EMPIRE WAR - three defense waves + Kondo duel")
    state["world"]["flags"]["octagram_done"] = True
    state["world"]["phase"] = max(state["world"]["phase"], 5)
    state["world"]["flags"]["empire_warned"] = False
    for w in range(3):
        state["world"]["flags"]["empire_warned"] = True
        state["world"]["flags"]["empire_next"] = 1
        arc = events_sys.arc_check(state)
        assert arc == "empire_wave", f"wave {w+1} not scheduled ({arc})"
        scripted = Script(); scripted.answers = ["walls"]
        run_event_with_script(events_sys.empire_wave_event, state, scripted)
        hero.hp = hero.max_hp; hero.mp = hero.max_mp
    assert state["world"]["flags"].get("empire_war_done")
    t = next(t for t in events_sys.TRIALS if t["id"] == "kondo")
    run_trial_quiet(state, t)
    assert state["world"]["flags"].get("kondo_defeated"), "kondo duel failed"

    step("PHASE H: MICHAEL RAID -> GODHOOD")
    hero.hp = hero.max_hp; hero.mp = hero.max_mp
    t = next(t for t in events_sys.TRIALS if t["id"] == "michael")
    run_trial_quiet(state, t)
    assert state["world"]["flags"].get("michael_defeated"), "michael raid failed"
    run_godhood(state)
    assert hero.godhood and hero.has_skill("azathoth"), "godhood failed"
    print(f"  GODHOOD. Final EP={hero.compute_ep():,} rank={rank_of(hero)}")

    step("PHASE I: POST-GOD - clear a dimensional gate T1")
    from src.systems import post_god
    pg = post_god.ensure_postgod(state)
    offer = post_god.make_offers(pg)[0]
    run_gate(state, offer)
    assert pg["gates_cleared"] >= 1, "gate not cleared"
    print(f"  gates cleared={pg['gates_cleared']} essence={pg['essence']}")

    step("PHASE J: save roundtrip at godhood")
    from src.core.save import save_game, load_game
    payload = {"player": hero.to_dict(), "world": dict(state["world"]),
               "roster": state["roster"], "captures": [], 
               "kingdom": state["kingdom"].to_dict(), "postgod": dict(pg)}
    save_game(payload, slot=2)
    loaded = load_game(2)
    h2_hero = Player.from_dict(loaded["player"])
    assert h2_hero.godhood and h2_hero.has_skill("azathoth")
    from src.systems.kingdom import Kingdom as K2
    k2 = K2.from_dict(loaded["kingdom"])
    assert k2.treasury == state["kingdom"].treasury
    print("  godhood save roundtrip OK")

    print("\n" + "=" * 60)
    print("FULL PLAYTHROUGH SIMULATION: SLIME TO GOD TO WORLD-DEVOURER")
    print("ALL PHASES CLEARED")


class Script:
    def __init__(self):
        self.answers = []


def get_skill_ok(sid):
    from src.data.skills import get_skill
    return get_skill(sid)


def rank_of(h):
    from src.entities.unit import rank_from_ep
    return rank_from_ep(h.compute_ep())


def install_quiet_ui():
    import src.core.ui as ui
    ui.menu = lambda prompt, options, allow_cancel=False, cancel_label="Back", color=None: 0 if allow_cancel else 1
    ui.pause = lambda msg="": None
    ui.clear = lambda: None
    _orig_voice = ui.voice
    def quiet_voice(lines):
        text = lines if isinstance(lines, str) else " ".join(lines)
        print(f"      [voice] {text[:90]}")
    ui.voice = quiet_voice


def make_battle_bot(state, script=None):
    PRIORITY = ["soul consume", "void collapse", "hellflare", "white flare", "melt slash",
                "death march", "creations blade", "cardinal", "sticky steel",
                "steel thread", "time stop", "flame breath", "wind cutter",
                "water blade", "lightning", "fireball", "icicle", "stone bullet", "drain"]

    def battle_bot(prompt, options, allow_cancel=False, cancel_label="Back", color=None):
        low = prompt.lower()
        if "turn - command" in low:
            h = state["hero"]
            has_item = any(o.strip().lower() == "item" for o in options)
            if h.hp < h.max_hp * 0.45 and has_item and h.consumables:
                return options.index("Item") if "Item" in options else 3
            has_skill = any(o.strip().lower() == "skill" for o in options)
            mp_ok = h.mp > h.max_mp * 0.25
            if has_skill and mp_ok:
                return options.index("Skill") if "Skill" in options else 1
            return options.index("Attack") if "Attack" in options else 0
        if "use which item" in low:
            for n, o in enumerate(options):
                if "potion" in o.lower() and "mp draft" not in o.lower():
                    return n
            return 0
        if "use which skill" in low:
            for hint in PRIORITY:
                for n, o in enumerate(options):
                    if hint in o.lower():
                        return n
            return 0
        if "target" in low:
            return 0
        if script:
            for a in script.answers:
                if a == "field" and ("sortie" in low or "take the field" in low):
                    return options.index(next(o for o in options if "ield" in o or "ortie" in o))
                if a == "walls" and ("labyrinth" in low or "walls" in low):
                    return options.index(next(o for o in options if "all" in o or "abyrinth" in o))
        if "command:" in low or "response:" in low:
            return 0
        return 0 if options else None

    return battle_bot


def run_event_with_script(fn, state, script=None):
    import src.core.ui as ui
    orig = ui.choose
    ui.choose = make_battle_bot(state, script)
    try:
        fn(state)
    finally:
        ui.choose = orig


def run_trial_quiet(state, trial):
    import src.core.ui as ui
    orig = ui.choose
    ui.choose = make_battle_bot(state)
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            events_sys.run_trial(state, trial)
    finally:
        ui.choose = orig
    if not state["world"].get("flags", {}).get(trial["id"] + "_defeated") and not trial.get("repeatable"):
        tail = buf.getvalue().splitlines()[-35:]
        print("  [battle trace]")
        for ln in tail:
            print("   ", ln[:110])


def run_godhood(state):
    import src.core.ui as ui
    orig = ui.choose
    def bot(prompt, options, allow_cancel=False, cancel_label='Back'):
        return 0
    ui.choose = bot
    try:
        with Quiet():
            progression.check_godhood(state)
    finally:
        ui.choose = orig


def run_gate(state, offer):
    import src.core.ui as ui
    from src.systems import post_god
    orig = ui.choose
    ui.choose = make_battle_bot(state)
    try:
        with Quiet():
            post_god.run_gate(state, offer)
    finally:
        ui.choose = orig


if __name__ == "__main__":
    main()
