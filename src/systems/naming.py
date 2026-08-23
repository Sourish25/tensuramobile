import random

from src.core import ui
from src.entities.unit import Subordinate
from src.data.monsters import MONSTERS
from src.data.skills import get_skill

PREFIX = ["Ri", "Go", "Ga", "Su", "Ha", "To", "Mi", "Ze", "Ku", "A", "E", "Ru", "So", "Ta", "Gu"]
MID = ["n", "b", "r", "z", "m", "l", "", ""]
SUF = ["a", "o", "u", "ta", "ru", "ga", "da", "mi", "ta", "ld", "rd"]


def random_name(rng=None):
    rng = rng or random.Random()
    return (rng.choice(PREFIX) + rng.choice(MID) + rng.choice(SUF)).title()


def name_cost(hero, species_key):
    t = MONSTERS[species_key]
    pct = hero.name_cost_pct(t["ep"])
    return int(max(5, hero.stats["mp"] * pct))


def can_name(hero, species_key):
    cost = name_cost(hero, species_key)
    remaining = hero.stats["mp"] - hero.mp_scar - cost
    return remaining >= hero.stats["mp"] * 0.06, cost


def naming_ceremony(state, species_key, level, source="capture", discount_pct=0.0):
    hero = state["hero"]
    t = MONSTERS[species_key]
    base_cost = name_cost(hero, species_key)
    cost = max(3, int(base_cost * (1.0 - discount_pct)))
    affordable = (hero.stats["mp"] - hero.mp_scar) - cost >= hero.stats["mp"] * 0.06

    ui.clear()
    ui.header("NAMING CEREMONY", f"{ui.GOLD_C}{hero.gold}g{ui.RESET} | MP scar {hero.mp_scar:.0f}")
    lines = [
        f"Species: {t['name']}  (Lv{level})",
        f"Magicule cost: {ui.M}{cost}{ui.RESET} of {hero.stats['mp']} total magicules",
        f"Current usable: {hero.max_mp}",
        "",
        ui.DIM + "Naming burns your own life force into another's soul. It never fully returns." + ui.RESET,
    ]
    for l in ui.panel(" OFFER A NAME ", lines, ui.M):
        print(l)

    if not affordable:
        print(ui.R + "Your magicules are too thin. Rest and recover first." + ui.RESET)
        ui.pause()
        return None

    opts = [f"Inscribe a name yourself", f"Let fate choose ({random_name()})"]
    c = ui.choose("Proceed?", opts, allow_cancel=True)
    if c is None:
        return None
    if c == 0:
        from src.core import webbridge
        nm = ""
        while not nm.strip():
            nm = (webbridge.ask_text("Name:") or "").strip()[:16]
            if not nm.strip():
                print(ui.R + "It needs a true name." + ui.RESET)
        name = nm
    else:
        name = opts[1].split("(")[1].rstrip(")")

    sub = Subordinate(name, species_key, level=level)
    evolved = sub.apply_named_form()
    sub.named_evolve_boost()
    sub.loyalty = 85
    hero.pay_name_cost(cost)

    roster = state.setdefault("roster", [])
    roster.append(sub.to_dict())

    msgs = [
        f"Naming executed. Magicules transferred: {cost}.",
        f"Individual [{name}] has received the name of [{hero.name}].",
    ]
    if evolved:
        msgs.append(f"Evolution complete. The individual has become a [{evolved}].")
    msgs.append(f"Loyalty established. [{name}] now follows you.")
    ui.voice(msgs)

    if hero.has_skill("great_sage"):
        ui.sage("Received. The soul corridor between you has opened. Shared growth will flow both ways.")

    assign = ui.choose(f"[{name}] awaits orders.", ["Join active party", "Hold in reserve"], allow_cancel=True)
    if assign == 0:
        set_party_slot(state, len(roster) - 1, join=True)
    ui.pause()
    return sub


def get_roster(state):
    return state.setdefault("roster", [])


def load_roster(state):
    subs = []
    for d in state.get("roster", []):
        subs.append(Subordinate.from_dict(d))
    return subs


def save_roster(state, subs):
    state["roster"] = [s.to_dict() for s in subs]


def party_subs(state):
    subs = load_roster(state)
    out = [s for i, s in enumerate(subs) if s.assignment == "party"][:3]
    save_roster(state, subs)
    return out


def set_party_slot(state, index, join):
    subs = load_roster(state)
    if join:
        in_party = sum(1 for s in subs if s.assignment == "party")
        if in_party >= 3:
            print(ui.R + "Active party is full (max 3 companions)." + ui.RESET)
            ui.pause()
            return
        subs[index].assignment = "party"
    else:
        if subs[index].assignment == "party":
            subs[index].assignment = "bench"
    save_roster(state, subs)


STANCES = ["aggressive", "balanced", "defensive", "support"]


def roster_menu(state):
    while True:
        subs = load_roster(state)
        ui.clear()
        ui.header("ROSTER", f"{len(subs)} named | Party {sum(1 for s in subs if s.assignment=='party')}/3")
        if not subs:
            body = ["No one bears your name yet.", "",
                    ui.DIM + "Spare defeated monsters and offer them a name," + ui.RESET,
                    ui.DIM + "or recruit willing souls at the goblin village." + ui.RESET]
            for l in ui.panel(" EMPTY ", body, ui.DIM):
                print(l)
            ui.pause()
            return
        lines = []
        for i, s in enumerate(subs):
            tag = {"party": "[PARTY]", "bench": "[reserve]"}.get(s.assignment, f"[{s.assignment}]")
            col = ui.BG if s.assignment == "party" else ui.DIM
            hp_bar = ui.bar(s.hp, s.max_hp, 12, show_nums=False)
            form = s.evolve_name or s.species.replace("_", " ").title()
            lines.append(
                f"{col}{i+1}. {s.glyph} {s.name:<14}{ui.RESET} {form:<20} Lv{s.level:<3} "
                f"ATK {s.stats['atk']:<4} MAG {s.stats['mag']:<4} AGI {s.stats['agi']:<4} "
                f"{tag} {s.stance:<10} Loyal {s.loyalty}%"
            )
            lines.append(f"     HP {hp_bar} {s.hp}/{s.max_hp}")
        for l in ui.panel(" NAMED FOLLOWERS ", lines, ui.G):
            print(l)
        opts = []
        if len(subs) > 0:
            opts.append("Toggle party membership")
            opts.append("Change combat stance")
            opts.append("Rename a follower")
        opts.append("Back")
        c = ui.choose("Manage:", opts, allow_cancel=False)
        if c == len(opts) - 1 or not subs:
            return
        si = ui.choose("Which follower?", [f"{s.name}" for s in subs], allow_cancel=True)
        if si is None:
            continue
        if c == 0:
            set_party_slot(state, si, join=subs[si].assignment != "party")
        elif c == 1:
            st_i = ui.choose("Stance:", STANCES, allow_cancel=True)
            if st_i is not None:
                subs[si].stance = STANCES[st_i]
                save_roster(state, subs)
        elif c == 2:
            from src.core import webbridge
            nm = (webbridge.ask_text("New name:") or "").strip()[:16]
            if nm:
                old = subs[si].name
                subs[si].name = nm
                save_roster(state, subs)
                ui.voice(f"The individual [{old}] shall henceforth be called [{nm}].")


def captures_add(state, species_key, level):
    caps = state.setdefault("captures", [])
    caps.append({"species": species_key, "level": level})


def captures_menu(state):
    hero = state["hero"]
    while True:
        caps = state.get("captures", [])
        ui.clear()
        ui.header("SPARED SOULS", f"{len(caps)} awaiting names")
        if not caps:
            for l in ui.text_panel(" NONE ", [
                    "You hold no spared monsters.",
                    "",
                    ui.DIM + "After a battle, choose 'Spare' instead of 'Devour'" + ui.RESET,
                    ui.DIM + "to bring a defeated foe back here for naming." + ui.RESET]):
                print(l)
            ui.pause()
            return
        lines = []
        for i, cp in enumerate(caps):
            t = MONSTERS[cp["species"]]
            ok, cost = can_name(hero, cp["species"])
            mark = ui.BG + "OK" + ui.RESET if ok else ui.R + "LOW MP" + ui.RESET
            lines.append(f"{i+1}. {t['glyph']} {t['name']} Lv{cp['level']}   cost {cost} MP  [{mark}]")
        for l in ui.panel(" AWAITING NAMES ", lines, ui.M):
            print(l)
        ci = ui.choose("Name which one?", [f"{MONSTERS[c['species']]['name']}" for c in caps], allow_cancel=True)
        if ci is None:
            return
        cp = caps[ci]
        ok, _ = can_name(hero, cp["species"])
        if not ok:
            print(ui.R + "Not enough magicules to spare." + ui.RESET)
            ui.pause()
            continue
        result = naming_ceremony(state, cp["species"], cp["level"])
        if result:
            caps.pop(ci)
