from src.core import ui
from src.data.skills import get_skill

SOULS_FOR_AWAKENING = 10000

HUMANISH = {"mercenary", "holy_knight", "imperial_guard", "kondo_guardian"}

RACE_AWAKEN_ULTIMATE = {
    "slime": ["raphael", "belzebuth", "soul_consume"],
    "goblin": ["amaterasu_u", "flame_breath_u"],
    "lizardman": ["nyarlathotep", "melt_slash"],
    "ogre": ["susano_oh", "creations_blade"],
    "direwolf": ["hastur", "time_stop"],
}

UNIQUE_TO_ULTIMATE = {
    "great_sage": "raphael",
    "predator": "belzebuth",
}

FESTIVAL_GRANTS = {
    "goblin": ["steel_thread", "fear_roar", "heal_minor"],
    "dire_wolf": ["wind_cutter", "lightning_bolt", "gravity_flight"],
    "orc_soldier": ["monstrous_str", "rot_aura", "body_slam"],
    "orc_rider": ["monstrous_str", "tempest_scale", "sharp_horn"],
    "horned_rabbit": ["sprint", "paralysis_breath", "sticky_steel_thread"],
    "giant_ant": ["paralysis_breath", "body_slam", "stone_bullet"],
    "black_spider": ["sticky_steel_thread", "poison_breath", "steel_thread"],
    "cave_centipede": ["paralysis_breath", "poison_breath", "claw_swipe"],
    "giant_bat": ["drain_touch", "ultrasonic_wave", "water_blade"],
    "lizardman": ["water_blade", "gravity_flight", "flame_aura"],
    "dire_alpha": ["wind_cutter", "lightning_bolt", "time_stop"],
}
DEFAULT_FESTIVAL = ["magic_sense", "flame_aura", "barrier_basic"]


def soul_value(enemy):
    base = max(10, int(enemy.ep_value / 10))
    if enemy.monster_id in HUMANISH:
        base *= 10
    return base


def gain_souls_from(state, enemies, multiplier=1):
    h = state["hero"]
    gained = sum(soul_value(e) for e in enemies) * multiplier
    h.souls += gained
    return gained


def replace_skill(unit, old_sid, new_sid):
    old_mastery = 0
    count = 0
    for sid in list(unit.skills.keys()):
        if sid == old_sid:
            old_mastery += unit.skills[sid]["mastery"]
            count += 1
            del unit.skills[sid]
    avg = old_mastery / count if count else 60
    unit.learn_skill(new_sid, mastery=max(60, avg))


def harvest_festival_cascade(state):
    roster = state.get("roster", [])
    if not roster:
        return []
    from src.entities.unit import Subordinate
    subs = [Subordinate.from_dict(d) for d in roster]
    lines = []
    for s in subs:
        for k in s.stats:
            s.stats[k] = int(s.stats[k] * 2.0) + 10
        s.hp = s.max_hp
        s.mp = s.max_mp
        pool = FESTIVAL_GRANTS.get(s.species, DEFAULT_FESTIVAL)
        granted = []
        for sid in pool:
            sk = get_skill(sid)
            if sk and not s.has_skill(sid):
                s.learn_skill(sid, mastery=50)
                granted.append(sk["name"])
            elif sk:
                s.skills[sid]["mastery"] = min(100.0, s.skills[sid]["mastery"] + 30)
                granted.append(f"{sk['name']} refined")
        s.loyalty = 100
        name = s.evolve_name or s.species.replace("_", " ").title()
        lines.append((s.name, name, granted))
    state["roster"] = [s.to_dict() for s in subs]
    return lines


def check_awakening(state):
    h = state["hero"]
    flags = state["world"].setdefault("flags", {})
    if h.demon_lord or h.souls < SOULS_FOR_AWAKENING:
        return False

    ui.clear()
    print()
    print(ui.BM + "The harvested souls stir inside you - ten thousand wills screaming as one." + ui.RESET)
    ui.pause()
    ui.voice([
        "Warning. Unique conditions have been met.",
        f"Soul quota fulfilled: {h.souls:,} / {SOULS_FOR_AWAKENING:,}.",
        "Initiating Harvest Festival.",
    ])
    print()
    ui.pause()

    h.demon_lord = True
    race_id = h.race_id
    for old, new in UNIQUE_TO_ULTIMATE.items():
        if h.has_skill(old):
            replace_skill(h, old, new)
            ui.voice(f"Unique skill [{get_skill(old)['name'] if get_skill(old) else old}] has evolved.")
            ui.voice(f"Confirmed. ULTIMATE SKILL [{get_skill(new)['name']}] acquired.")
    for uid in RACE_AWAKEN_ULTIMATE.get(race_id, []):
        if not h.has_skill(uid):
            h.learn_skill(uid, mastery=70)
            ui.voice(f"ULTIMATE SKILL [{get_skill(uid)['name']}] awakened.")

    for k in h.stats:
        h.stats[k] = int(h.stats[k] * 2.2) + 20
    h.hp = h.max_hp
    h.mp = h.max_mp

    stage_names = {
        "slime": "Demon Slime", "goblin": "Oni King", "lizardman": "Dragon Lord-tier",
        "ogre": "Awakened Oni", "direwolf": "Divine Wolf",
    }
    print()
    ui.voice(f"Evolution complete. The individual [{h.name}] has been reborn as a [{stage_names.get(race_id, 'Awakened')}].")
    print()

    cascade = harvest_festival_cascade(state)
    ui.voice("The Festival flows through every soul bound to your name...")
    for sname, form, granted in cascade:
        print(f"  {ui.BG}{sname}{ui.RESET} ({form}) receives the blessing: {', '.join(granted)}.")
    if cascade:
        ui.voice("Your named followers have evolved. The Harvest Festival concludes.")
    else:
        print(ui.DIM + "(No named followers yet to receive the blessing.)" + ui.RESET)

    state["world"]["phase"] = max(state["world"]["phase"], 4)
    state["world"]["flags"]["awakened"] = True
    k_add = 5000
    h.gold += k_add
    print()
    print(ui.GOLD_C + f"The world takes notice. Walpurgis will call soon. (+{k_add}g spoils of fear)" + ui.RESET)
    ui.pause()
    return True


def check_godhood(state):
    h = state["hero"]
    flags = state["world"].setdefault("flags", {})
    if h.godhood or not h.demon_lord or not flags.get("michael_defeated"):
        return False

    ui.clear()
    print()
    for l in ui.text_panel(" THE ADMINISTRATOR'S SEAT ",
                           "Michael's authority dissolves into your hands like snow in starlight. "
                           "Somewhere beyond the sky, a door no mortal built swings open.", ui.BY):
        print(l)
    print()
    ui.pause()
    ui.voice([
        "Ultimate Dominion seized.",
        "Administrator rights transferred to individual [" + h.name + "].",
        "Detected: dormant authority [Azathoth]. Merge proposed.",
    ])
    print()
    c = ui.choose("Merge Raphael and Belzebuth into Azathoth, God of the Void?", [
        "Become.",
        "Not yet",
    ])
    if c != 0:
        ui.voice("Merge deferred. The seat waits.")
        return False

    h.godhood = True
    if not h.has_skill("azathoth"):
        h.learn_skill("azathoth", mastery=100)
    ui.voice("ULTIMATE SKILL [Azathoth, God of the Void] acquired.")
    for k in h.stats:
        h.stats[k] = int(h.stats[k] * 3) + 100
    h.hp = h.max_hp
    h.mp = h.max_mp
    state["world"]["phase"] = max(state["world"]["phase"], 8)
    state["world"]["flags"]["godhood"] = True
    gz = "celestial_gates"
    unlocked = state["world"].setdefault("unlocked_zones", [])
    if gz not in unlocked:
        unlocked.append(gz)
    print()
    for l in ui.text_panel(" GODHOOD ",
                           "You are no longer a monster, a demon lord, or even a dragon. "
                           "You are the thing the World reaches toward when it dreams. "
                           "And still - the grind goes on. Countless worlds wait behind the Gates.", ui.BY):
        print(l)
    print()
    ui.voice("New area unlocked: The Celestial Gates.")
    ui.pause()
    return True
