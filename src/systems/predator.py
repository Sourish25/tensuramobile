import random

from src.core import ui
from src.data.skills import get_skill, RECIPES
from src.data.items import ITEMS


def can_devour(hero):
    if hero.has_skill("predator") or hero.has_skill("absorb"):
        return True
    return False


def devour_roll(rng, hero, enemy):
    lv_gap = hero.level - enemy.level
    chance = 45 + lv_gap * 6 + hero.stats.get("luk", 5) * 1.2
    if enemy.is_boss:
        chance -= 15
    chance = max(8, min(92, chance))
    return rng.random() * 100 < chance


def devour_one(state, e):
    hero = state["hero"]
    rng = random.Random()
    gained_skills = []
    materials = {}
    forms = []

    ui.clear()
    ui.header("PREDATOR", "Devour")
    art = f"{e.color}{e.glyph} {e.name}{ui.RESET}   (Lv{e.level})"
    print(art.center(ui.WIDTH))
    print()
    print(f"{ui.DIM}{e.desc or 'A slain monster.'}{ui.RESET}")
    print()

    hero.devour_count += 1
    mp_refund = max(4, int(hero.max_mp * 0.08))
    hero.mp = min(hero.max_mp, hero.mp + mp_refund)

    stealable = list(e.stealable)
    if e.is_boss and e.signature_skill and e.signature_skill not in stealable:
        stealable.insert(0, e.signature_skill)
    for sid in stealable:
        guaranteed = (e.is_boss and sid == e.signature_skill)
        if guaranteed or devour_roll(rng, hero, e):
            if not hero.has_skill(sid):
                s = get_skill(sid)
                if s:
                    hero.learn_skill(sid)
                    gained_skills.append(sid)
                    ui.voice(f"Skill [{s['name']}] successfully acquired.")
            else:
                d = hero.skills[sid]
                if d["mastery"] < 100:
                    add = min(100 - d["mastery"], 12 if guaranteed else 7)
                    d["mastery"] += add
                    ui.voice(f"[{get_skill(sid)['name']}] analysis deepened: mastery {d['mastery']:.0f}%.")

    form_name = e.name + " Mimicry"
    if form_name not in hero.mimic_forms and (e.is_boss or rng.random() < 0.35):
        hero.mimic_forms.append(form_name)
        forms.append(form_name)
        ui.voice(f"Mimicry data stored: [{form_name}].")

    for mat, _ in getattr(e, "drops", []):
        materials[mat] = materials.get(mat, 0) + 1
    hero.stomach[e.monster_id] = hero.stomach.get(e.monster_id, 0) + 1

    return {"skills": gained_skills, "materials": materials, "forms": forms}


def check_combinations(hero):
    unlocked = []
    known = set(hero.skills.keys())
    for a, b, child in RECIPES:
        if child in known:
            continue
        if a in known and b in known:
            ma = hero.skills[a]["mastery"]
            mb = hero.skills[b]["mastery"]
            if ma >= 60 and mb >= 60:
                from src.data.skills import COMBO_SKILLS
                combo = COMBO_SKILLS.get(child)
                if combo:
                    hero.learn_skill(child, mastery=50)
                    for p in (a, b):
                        hero.skills[p]["mastery"] = min(100.0, hero.skills[p]["mastery"])
                        if hero.skills[p]["mastery"] >= 100:
                            pass
                    gp = combo.get("grants_passive")
                    unlocked.append((child, gp))
    return unlocked


def offer_combination_menu(state):
    hero = state["hero"]
    while True:
        ready = []
        known = set(hero.skills.keys())
        for a, b, child in RECIPES:
            if child in known:
                continue
            if a in known and b in known and hero.skills[a]["mastery"] >= 60 and hero.skills[b]["mastery"] >= 60:
                from src.data.skills import COMBO_SKILLS
                combo = COMBO_SKILLS.get(child)
                if combo:
                    ready.append((a, b, child))
        if not ready:
            return
        ui.clear()
        ui.header("GREAT SAGE", "Skill Synthesis")
        opts = []
        for a, b, child in ready:
            combo_name = get_skill(child)["name"]
            opts.append(f"{get_skill(a)['name']} ({hero.skills[a]['mastery']:.0f}%) + "
                        f"{get_skill(b)['name']} ({hero.skills[b]['mastery']:.0f}%) -> {combo_name}")
        i = ui.choose("Synthesize which skill?", opts, allow_cancel=True)
        if i is None:
            return
        a, b, child = ready[i]
        hero.learn_skill(child, mastery=50)
        ui.voice([
            f"Detected compatible skill structures.",
            f"Combining [{get_skill(a)['name']}] and [{get_skill(b)['name']}].",
            f"Unique synthesis successful.",
            f"New extra skill [{get_skill(child)['name']}] acquired.",
        ])


def stomach_menu(state):
    hero = state["hero"]
    while True:
        ui.clear()
        ui.header("STOMACH", "Timeless Storage")
        lines = []
        total_items = sum(hero.stomach.values()) + sum(hero.materials.values())
        if not hero.stomach and not hero.materials:
            lines.append("(empty)")
        else:
            for mid, n in sorted(hero.stomach.items(), key=lambda x: -x[1])[:12]:
                lines.append(f"Corpse x{n}: {mid.replace('_', ' ').title()}")
            lines.append("")
            for m, n in sorted(hero.materials.items()):
                it = ITEMS.get(m, {})
                lines.append(f"{it.get('name', m)} x{n}  ({ui.GOLD_C}{it.get('value', 0)}g each{ui.RESET})")
        for l in ui.panel(" Contents ", [f"{total_items} items absorbed", ""] + lines[:24], ui.M):
            print(l)
        opts = ["Sell all duplicate materials", "Back"]
        c = ui.choose("Stomach actions:", opts)
        if c == 0:
            gold = 0
            for m, n in list(hero.materials.items()):
                v = ITEMS.get(m, {}).get("value", 0)
                keep = 1
                sell = n - keep
                if sell > 0:
                    gold += v * sell
                    hero.materials[m] = keep
            hero.gold += gold
            ui.voice(f"Materials sold to traveling merchants. +{gold} gold.")
            continue
        return
