import random

from src.core import ui
from src.data import monsters as mdata
from src.data import items as idata
from src.data import buildings as bdata
from src.data.skills import get_skill, mastery_rank
from src.data import races as races_data
from src.entities.unit import enemy_from_template, rank_from_ep
from src.systems import combat
from src.systems import predator as predator_sys
from src.systems import naming as naming_sys
from src.systems import progression
from src.systems import events as events_sys
from src.systems import post_god
from src.screens import kingdom as kingdom_screen


def status_view(state):
    h = state["hero"]
    ui.clear()
    ep = h.compute_ep()
    lines = [
        f"{h.color}{h.glyph} {h.name}{ui.RESET}  -  {ui.BW}{h.stage_name}{ui.RESET}  (Race: {races_data.RACES[h.race_id]['name']})",
        f"Level {h.level}   XP {h.xp:.0f}/{h.xp_to_next()}  [{ui.bar(h.xp, h.xp_to_next(), 20, color=ui.XP_C, show_nums=False)}]",
        f"HP [{ui.bar(h.hp, h.max_hp, 24)}]   MP [{ui.bar(h.mp, h.max_mp, 18, color=ui.MP_C)}]",
        f"EP {ep:,}   Guild Rank Estimate: {ui.GOLD_C}{rank_from_ep(ep)}{ui.RESET}",
        "",
        f"ATK {h.stats['atk']+h.weapon_atk():>4}  DEF {h.stats['def']+h.armor_def():>4}  MAG {h.stats['mag']:>4}  SPR {h.stats['spr']:>4}  AGI {h.stats['agi']:>4}",
        f"Weapon: {idata.ITEMS[h.gear['weapon']]['name'] if h.gear['weapon'] else '(none)'}    Armor: {idata.ITEMS[h.gear['armor']]['name'] if h.gear['armor'] else '(none)'}",
        f"Gold {ui.GOLD_C}{h.gold}{ui.RESET}   Souls {ui.M}{h.souls:,}{ui.RESET}   Devours {h.devour_count}   Kills {h.kills}   MP scar {h.mp_scar:.0f}/{h.stats['mp']}",
    ]
    titles = []
    if h.demon_lord:
        titles.append(ui.BM + "Demon Lord" + ui.RESET)
    if h.godhood:
        titles.append(ui.BY + "GOD" + ui.RESET)
    if titles:
        lines.insert(1, "Title: " + " | ".join(titles))
    for l in ui.panel(" STATUS ", lines, h.color):
        print(l)
    ui.pause()


def skills_menu(state):
    h = state["hero"]
    while True:
        ui.clear()
        tiers = {}
        for sid, d in h.skills.items():
            s = get_skill(sid)
            if s:
                tiers.setdefault(s["tier"], []).append((sid, s, d))
        lines = []
        tcolors = {"intrinsic": ui.C, "common": ui.W, "extra": ui.BG, "unique": ui.BM, "ultimate": ui.BY}
        for tier in ("intrinsic", "common", "extra", "unique", "ultimate"):
            entries = tiers.get(tier, [])
            if not entries:
                continue
            lines.append(f"{tcolors[tier]}-- {tier.upper()} --{ui.RESET}")
            for sid, s, d in sorted(entries, key=lambda x: x[2]["mastery"], reverse=True):
                m = d["mastery"]
                lines.append(f"  {tcolors[tier]}{s['name']:<28}{ui.RESET} {ui.bar(m, 100, 14, color=tcolors[tier], show_nums=False)} {m:>5.0f}%  {mastery_rank(m)}")
            lines.append("")
        for l in ui.panel(f" SKILLS - {len(h.skills)} known ", lines, ui.B):
            print(l)
        c = ui.choose("Skills:", ["Synthesize (Great Sage)", "Back"])
        if c == 0:
            predator_sys.offer_combination_menu(state)
            continue
        return


def gain_rewards(state, result):
    h = state["hero"]
    xp = result["xp"]
    leveled = h.gain_xp(xp)
    ui.voice("Confirmed. Experience points accumulated. Individual status rising.")
    for lv in leveled:
        kind = h.level_up()
        evo_changed = h.check_evolution()
        stage = races_data.evolution_stage(h.race_id, h.level)
        msgs = [f"Individual [{h.name}] has reached Level {lv}."]
        if kind == "latent":
            r = races_data.RACES[h.race_id]
            names = []
            for sid in r["latent_unique"]:
                s = get_skill(sid)
                if s:
                    names.append(s["name"])
            msgs.insert(1, f"Unique skill awakened: {', '.join(names)}.")
        if evo_changed:
            msgs.append(f"Evolution complete. The individual [{h.name}] has become [{stage['name']}].")
        ui.voice(msgs)
        if evo_changed:
            for sid in stage.get("grants", []):
                s = get_skill(sid)
                if s:
                    h.learn_skill(sid)
                    ui.voice(f"Intrinsic evolution gift: [{s['name']}] acquired.")

    share = int(xp * 0.6)
    subs = naming_sys.load_roster(state)
    changed = False
    for i, s in enumerate(subs):
        if s.assignment != "party" or not s.alive:
            continue
        slv = s.gain_xp(share)
        s.loyalty = min(100, s.loyalty + 1)
        if slv:
            ui.voice(f"[{s.name}] grows alongside you: Level {'-> Lv'.join(str(x) for x in slv)}.")
            feedback = int(s.xp_to_next() * 0.06)
            if feedback > 0:
                h.gain_xp(feedback)
                print(ui.DIM + f"  Food Chain: [{s.name}]'s growth feeds back to you (+{feedback} XP)." + ui.RESET)
        changed = True
    if changed:
        naming_sys.save_roster(state, subs)


def revive_party(state):
    subs = naming_sys.load_roster(state)
    changed = False
    for s in subs:
        if s.assignment == "party" and not s.alive:
            s.hp = max(1, int(s.max_hp * 0.30))
            s.mp = int(s.max_mp * 0.3)
            print(ui.DIM + f"[{s.name}] slowly reknits their wounds..." + ui.RESET)
            changed = True
    if changed:
        naming_sys.save_roster(state, subs)


def postbattle_souls(state, enemies):
    h = state["hero"]
    for e in enemies:
        if e.alive:
            continue
        t = mdata.MONSTERS[e.monster_id]
        sparable = bool(t.get("sparable")) or not e.is_boss
        opts = ["Devour - absorb its essence"]
        if sparable:
            opts.append("Spare - hold its fading soul for naming")
        opts.append("Leave it")
        c = ui.choose(f"The {e.name}'s remains:", opts)
        if c == 0:
            dev = predator_sys.devour_one(state, e)
            for mat, n in dev["materials"].items():
                h.materials[mat] = h.materials.get(mat, 0) + n
        elif sparable and c == 1:
            naming_sys.captures_add(state, e.monster_id, e.level)
            print(ui.M + f"The {e.name}'s fading spirit is bound to you." + ui.RESET)


def battle_flow(state, monster_ids, location):
    h = state["hero"]
    scale = 1 + (state["world"]["floor"] - 1) * 0.06
    enemies = [enemy_from_template(mid, scale) for mid in monster_ids]
    allies = naming_sys.party_subs(state)
    b = combat.Battle(h, allies, enemies, location=location)
    result = b.run()
    out = {"enemies": enemies, "result": result["result"]}
    if result["result"] == "win":
        h.kills += len(enemies)
        gain_rewards(state, result)
        souls = progression.gain_souls_from(state, enemies)
        if souls > 0:
            print(f"{ui.M}Souls drift into you: +{souls} (total {h.souls:,}){ui.RESET}")
        progression.check_awakening(state)
        drops = result.get("drops", {})
        if drops:
            dl = [f"{idata.ITEMS[m]['name']} x{n}" for m, n in drops.items()]
            for l in ui.panel(" SPOILS ", [f"+{result['xp']} XP", ", ".join(dl)], ui.Y):
                print(l)
        revive_party(state)
        postbattle_souls(state, enemies)
        combos = predator_sys.check_combinations(h)
        for child, gp in combos:
            ui.voice([
                "Detected compatible skill structures.",
                f"[{get_skill(child)['name']}] successfully synthesized.",
            ])
        predator_sys.offer_combination_menu(state)
    elif result["result"] == "lose":
        defeat_flow(state)
    else:
        print(ui.DIM + "You slip away into the wilds..." + ui.RESET)
        ui.pause()
        revive_party(state)
    return out


def defeat_flow(state):
    h = state["hero"]
    lost = h.gold // 2
    h.gold -= lost
    h.hp = max(1, int(h.max_hp * 0.3))
    h.mp = max(0, int(h.max_mp * 0.2))
    if state["world"]["zone"] == "goblin_village":
        state["world"]["zone"] = "jura_plains"
    state["world"]["floor"] = 1
    ui.voice("Critical failure detected...")
    print()
    for l in ui.text_panel(" DARKNESS ",
                           "Your body scatters into motes of magicules. Something ancient drags your "
                           "essence back toward safety. You reform slowly... "
                           f"{lost} gold slipped away.", ui.R):
        print(l)
    print()
    revive_party(state)
    ui.pause()


def on_boss_defeated(state, zid, boss_id):
    zone = mdata.ZONES[zid]
    nxt = zone.get("unlock") or []
    if isinstance(nxt, str):
        nxt = [nxt]
    if boss_id == "tempest_serpent":
        ui.voice([
            "The guardian of the depths has fallen.",
            "Its magicule core saturates your body.",
            "Confirmed. The path beyond the cave is now open.",
        ])
        print()
        for l in ui.text_panel(" THE WORLD OPENS ",
                               "Sunlight pours through the cave mouth for the first time. The Great "
                               "Jura Forest stretches endlessly before you. Somewhere out there: "
                               "goblins in need of a leader, beasts to hunt, and a destiny only "
                               "you can name.", ui.Y):
            print(l)
    elif boss_id == "dire_alpha":
        ui.voice("The pack bows its head. The forest edge falls silent.")
    for zid2 in nxt:
        unlocked = state["world"].setdefault("unlocked_zones", [])
        if zid2 not in unlocked:
            unlocked.append(zid2)
            print()
            print(f"{ui.BY}>> New area unlocked: {mdata.ZONES[zid2]['name']} <<{ui.RESET}")
    state["world"]["phase"] = max(state["world"]["phase"], 1)
    ui.pause()


def explore(state):
    h = state["hero"]
    zid = state["world"]["zone"]
    zone = mdata.ZONES[zid]
    floor = state["world"]["floor"]

    if zone.get("village"):
        village_explore(state)
        return

    slain = state["world"].setdefault("bosses_slain", [])
    loc_name = f"{zone['name']} B{floor}F" if zid == "sealed_cave" else f"{zone['name']} Area {floor}"

    boss_id = zone["bosses"].get(floor)
    if boss_id and boss_id not in slain:
        boss = mdata.MONSTERS[boss_id]
        print(f"{ui.BR}A monstrous presence blocks the way...{ui.RESET}")
        print(f"{ui.ENEMY_C}{boss['glyph']} {boss['name']}{ui.RESET} - {boss.get('desc', '')}")
        c = ui.choose("Face it?", ["Fight!", "Retreat"])
        if c == 0:
            out = battle_flow(state, [boss_id], loc_name + " - BOSS")
            if out.get("result") == "win":
                slain.append(boss_id)
                on_boss_defeated(state, zid, boss_id)
        return

    enc_table = [e for e in zone["encounters"] if e["floor"] == floor]
    enc = mdata.zone_encounter(zid, floor, random) if enc_table else None
    if enc is None:
        finds_cave = [
            ("You find a patch of hipokute grass glowing faintly.", ("hipokute_grass", 2)),
            ("A small magic crystal sits embedded in stone. You pry it free.", ("magic_crystal_shard", 1)),
            ("Nothing stirs. The silence feels heavy.", None),
            ("Water drips somewhere far off. You drink and feel slightly restored.", "heal"),
        ]
        finds_forest = [
            ("You fell a few trees and trim the timber for transport.", ("timber", 3)),
            ("You quarry loose stone blocks near the streambed.", ("stone", 2)),
            ("Hipokute flowers sway in the breeze. You gather an armful.", ("hipokute_grass", 2)),
            ("Nothing stirs. Birds circle lazily overhead.", None),
        ]
        finds = finds_cave if zid == "sealed_cave" else finds_forest
        msg, fx = random.choice(finds)
        print(msg)
        if fx == "heal":
            h.hp = min(h.max_hp, h.hp + int(h.max_hp * 0.15))
        elif fx:
            mat, n = fx
            h.materials[mat] = h.materials.get(mat, 0) + n
        deepest = state["world"].setdefault("deepest_floor", 1)
        if floor > deepest:
            state["world"]["deepest_floor"] = floor
        if state.get("kingdom"):
            state["kingdom"].deepest_floor = max(state["kingdom"].deepest_floor, deepest)
        if random.random() < 0.25 and floor < zone["floors"]:
            state["world"]["floor"] = floor + 1
            print(f"\n{ui.C}You discover a path deeper in ({floor + 1}).{ui.RESET}")
        ui.pause()
        return
    battle_flow(state, enc, loc_name)


def village_explore(state):
    flags = state["world"].setdefault("flags", {})
    if not flags.get("village_met"):
        first_meeting(state)
        return
    if not flags.get("village_founded"):
        found_village_offer(state)
        return
    print("The village bustles softly. Goblins nod as you pass.")
    print(ui.DIM + "(Use the village services from the main menu.)" + ui.RESET)
    ui.pause()


def first_meeting(state):
    h = state["hero"]
    print()
    for l in ui.text_panel(" SMOKE ON THE WIND ",
                           "A thin column of smoke rises ahead. You find a cluster of crude huts - "
                           "and carnage. Black wolves circle what remains of a goblin village. A "
                           "wounded goblin elder props himself against a broken spear and stares "
                           "at you without fear.", ui.Y):
        print(l)
    print()
    c = ui.choose("The elder rasps: 'Help us... please.'", [
        "Fight the wolf pack",
        "Turn away",
    ])
    if c == 1:
        print(ui.DIM + "You melt into the brush. The howling fades behind you." + ui.RESET)
        ui.pause()
        return
    state["world"]["flags"]["village_met"] = True
    out = battle_flow(state, ["dire_wolf", "dire_wolf"], "Goblin Village Defense")
    if out.get("result") != "win":
        return
    print()
    for l in ui.text_panel(" AFTERMATH ",
                           "The survivors emerge - perhaps a hundred goblins, gaunt and terrified. "
                           "The old chief kneels before you.", ui.Y):
        print(l)
    print()
    print(f"{ui.BW}\"Great one... we have watched the strong devour the weak for too long.\"")
    print(f"{ui.BW}\"Grant us your name. We will become your sword, your shield, your people.\"{ui.RESET}")
    print()
    ok, cost = naming_sys.can_name(h, "goblin")
    discount = 0.5 if not ok else 0.0
    naming_sys.naming_ceremony(state, "goblin", level=2, discount_pct=discount)
    state["world"]["flags"]["village_founded"] = True
    state["world"].setdefault("unlocked_zones", [])
    refresh_recruit_pool(state)
    h.gold += 100
    ensure_kingdom(state)
    print()
    ui.voice("A settlement accepts your dominion. Your legend begins.")
    print(f"{ui.GOLD_C}The villagers scrape together 100 gold as tribute.{ui.RESET}")
    ui.pause()


def found_village_offer(state):
    h = state["hero"]
    print()
    print(f"{ui.BW}The goblin elder waits at the village center, watching you expectantly.{ui.RESET}")
    c = ui.choose("Grant them a name?", ["Hold the naming ceremony", "Not yet"])
    if c == 0:
        ok, cost = naming_sys.can_name(h, "goblin")
        discount = 0.5 if not ok else 0.0
        naming_sys.naming_ceremony(state, "goblin", level=2, discount_pct=discount)
        state["world"]["flags"]["village_founded"] = True
        refresh_recruit_pool(state)
        h.gold += 100
        ensure_kingdom(state)
        ui.voice("A settlement accepts your dominion. Your legend begins.")
        print(f"{ui.GOLD_C}The villagers offer 100 gold as tribute.{ui.RESET}")
        ui.pause()


def ensure_kingdom(state):
    if state.get("kingdom") is None:
        from src.systems.kingdom import Kingdom
        state["kingdom"] = Kingdom()
        ui.voice([
            "A dominion requires governance.",
            "Confirmed. Realm administration systems established.",
            "Access them via [Tempest Governance] while at the settlement.",
        ])
        ui.pause()


def random_daily_event(state):
    k = state["kingdom"]
    roll = random.random()
    hostile = [fid for fid, rel in k.relations.items() if rel <= -30]
    if hostile and k.pending_siege is None and roll < 0.30:
        fid = random.choice(hostile)
        k.pending_siege = {"faction": fid, "days": random.randint(2, 3)}
        f = bdata.FACTIONS[fid]
        k.add_history(f"Invasion warning: {f['name']}.")
        print(ui.BR + f"Scouts report {f['name']} forces massing! Invasion within days!" + ui.RESET)
        ui.pause()
        return
    pool = []
    if k.has("trading_post"):
        pool.append(("caravan", 22))
    pool.append(("diplomat", 16))
    pool.append(("migration", 12))
    if k.happiness < 45:
        pool.append(("unrest", 10))
    total = sum(w for _, w in pool)
    r = random.uniform(0, total)
    acc = 0
    chosen = None
    for name, w in pool:
        acc += w
        if r <= acc:
            chosen = name
            break

    if chosen == "caravan":
        bonus_gold = 0
        for m, n in list(state["hero"].materials.items()):
            sell = n - 1
            if sell > 0:
                bonus_gold += int(idata.ITEMS.get(m, {}).get("value", 0) * 1.5) * sell
                state["hero"].materials[m] = 1
        if bonus_gold > 0:
            k.treasury += bonus_gold
            k.add_history(f"Caravan bought surplus goods (+{bonus_gold}g to treasury).")
            print(ui.GOLD_C + f"A merchant caravan passes through! Surplus materials sold to the realm: +{bonus_gold}g treasury." + ui.RESET)
        else:
            print("A caravan passes by but you have no surplus to sell.")
        ui.pause()
    elif chosen == "diplomat":
        fid = random.choice(list(bdata.FACTIONS.keys()))
        delta = random.randint(3, 7)
        k.relations[fid] = min(100, k.relations[fid] + delta)
        k.add_history(f"{bdata.FACTIONS[fid]['name']} sent a friendly envoy (+{delta} rel).")
        print(ui.C + f"An envoy from {bdata.FACTIONS[fid]['name']} visits: relations +{delta}." + ui.RESET)
        ui.pause()
    elif chosen == "migration":
        species = random.choice(["horned_rabbit", "dire_wolf", "giant_ant"])
        naming_sys.captures_add(state, species, random.randint(1, 3))
        t = mdata.MONSTERS[species]
        k.add_history(f"A wandering {t['name']} sought sanctuary.")
        print(ui.M + f"A lost {t['name']} wanders into your lands seeking shelter. (See Spared Souls.)" + ui.RESET)
        ui.pause()
    elif chosen == "unrest":
        k.happiness -= 5
        k.add_history("Grumbling among the workers.")
        print(ui.Y + "Workers grumble about conditions. Happiness -5." + ui.RESET)
        ui.pause()


def siege_event(state, faction_id):
    k = state["kingdom"]
    h = state["hero"]
    squad = mdata.FACTION_SQUADS.get(faction_id, ["mercenary"])
    defense_cut = min(40, int(k.city_defense() / 12))
    f = bdata.FACTIONS[faction_id]
    print()
    for l in ui.text_panel(f" SIEGE OF TEMPEST ",
                           f"{f['name']} marches on your settlement! "
                           f"City defenses ({k.city_defense()}) blunt their assault by {defense_cut}%.", ui.R):
        print(l)
    print()
    c = ui.choose("Command the defense?", [
        "Take the field personally",
        "Let the walls hold (auto-resolve)",
    ])
    scale = max(1.0, (state["world"]["day"]) / 18.0) * (1 - defense_cut / 100.0)
    enemies = [enemy_from_template(mid, scale) for mid in squad]
    if c == 0:
        allies = naming_sys.party_subs(state)
        b = combat.Battle(h, allies, enemies, location="SIEGE OF TEMPEST")
        result = b.run()
        win = result["result"] == "win"
        if win:
            h.kills += len(enemies)
            gain_rewards(state, {"xp": sum(e.xp_reward for e in enemies), "drops": {}})
            revive_party(state)
    else:
        power = sum(e.ep_value for e in enemies)
        win = k.city_defense() * 55 + h.compute_ep() > power * 1.15
        print(f"\nYour forces clash with the invaders beyond the walls...")
    if win:
        loot = int(power if False else 150 + 60 * len(enemies))
        k.treasury += loot
        k.relations[faction_id] = min(100, k.relations[faction_id] + 8)
        k.add_history(f"Repelled the siege by {f['name']} (+{loot}g spoils).")
        ui.voice(f"The invaders are broken! Spoils: {loot}g. Relations with {f['name']}: +8.")
    else:
        destroyed, plunder, loss = k.siege_damage(random.Random())
        dname = bdata.BUILDINGS[destroyed]["name"] if destroyed else "the outskirts"
        k.add_history(f"SIEGE LOST to {f['name']}: {dname} ruined, {plunder}g plundered, {loss} dead.")
        ui.voice([
            "The walls are breached...",
            f"Lost: {dname}, treasury plundered {plunder}g, {loss} souls gone.",
        ])
    ui.pause()


def tournament_event(state):
    h = state["hero"]
    print()
    for l in ui.text_panel(" TEMPEST TOURNAMENT ",
                           "Fighters gather for a martial exhibition before roaring crowds. "
                           "Three victories would make your legend ring across the forest.", ui.Y):
        print(l)
    c = ui.choose("Enter the arena?", ["Enter", "Decline"])
    if c != 0:
        return
    roster = ["dire_alpha", "armorsaurus", "orc_general"]
    for i, mid in enumerate(roster, 1):
        out = battle_flow(state, [mid], f"Tournament Round {i}")
        if out.get("result") != "win":
            print(ui.R + "Eliminated from the tournament." + ui.RESET)
            ui.pause()
            return
    prize = 250
    state["hero"].gold += prize
    state["kingdom"].treasury += 200
    state["kingdom"].happiness = min(98, state["kingdom"].happiness + 8)
    state["kingdom"].add_history("Tournament champion crowned (+8 happiness).")
    ui.voice(f"CHAMPION! Prize: {prize}g personal, 200g to the treasury. The crowd roars your name!")
    ui.pause()


def rest(state):
    h = state["hero"]
    h.hp = h.max_hp
    h.mp = h.max_mp
    scar_mult = 1.4 if (state.get("kingdom") and state["kingdom"].has("hot_spring")) else 1.0
    healed = 0.0
    for _ in range(1):
        healed += h.recover_scar_on_rest() * scar_mult / 1.4
    state["world"]["day"] += 1
    if state["world"].get("recruit_pool") is not None and state["world"]["zone"] == "goblin_village":
        refresh_recruit_pool(state)
    print(f"{ui.BG}You settle into stillness and let the ambient magicules seep in.{ui.RESET}")
    print(f"Fully restored. Magicule scar eased by {healed:.0f}. Day {state['world']['day']}.")
    k = state.get("kingdom")
    founded = state["world"]["flags"].get("village_founded")
    if k is None and founded:
        ensure_kingdom(state)
        k = state["kingdom"]
    arc = events_sys.arc_check(state)
    if arc == "orc_war":
        events_sys.orc_war_event(state)
    elif arc == "walpurgis":
        events_sys.walpurgis_event(state)
    elif arc == "empire_wave":
        events_sys.empire_wave_event(state)
    if k:
        events = k.daily_tick(h, state["world"]["day"])
        print()
        for kind, data in events:
            if kind == "income":
                print(ui.DIM + f"  Treasury +{data}" + ui.RESET)
            elif kind == "build_done":
                print(ui.BG + f"  ** {data} **" + ui.RESET)
            elif kind == "growth":
                print(ui.BC + f"  Population rising: {data}" + ui.RESET)
            elif kind == "famine":
                print(ui.R + f"  {data}" + ui.RESET)
            elif kind == "research":
                print(ui.DIM + f"  {data}" + ui.RESET)
            elif kind == "delivery":
                print(ui.DIM + f"  {data}" + ui.RESET)
            elif kind == "siege":
                siege_event(state, data)
        non_siege = [e for e in events if e[0] != "siege"]
        if any(e[0] in ("build_done", "growth", "famine") for e in non_siege):
            pass
        if not any(e[0] == "siege" for e in events):
            random_daily_event(state)
        if k.has("colosseum") and random.random() < 0.20 and state["world"]["day"] % 3 == 0:
            tournament_event(state)
    ui.pause()


def refresh_recruit_pool(state):
    pool = []
    weights = [("goblin", 40), ("dire_wolf", 25), ("horned_rabbit", 20), ("giant_ant", 15)]
    n = random.randint(2, 3)
    species = [w[0] for w in weights]
    probs = [w[1] for w in weights]
    for _ in range(n):
        sp = random.choices(species, probs)[0]
        lv = random.randint(1, 3)
        pool.append({"species": sp, "level": lv})
    state["world"]["recruit_pool"] = pool
    return pool


def recruit_menu(state):
    h = state["hero"]
    pool = state["world"].get("recruit_pool")
    if pool is None:
        pool = refresh_recruit_pool(state)
    while True:
        ui.clear()
        ui.header("RECRUITMENT", "Monsters drawn to your growing legend")
        if not pool:
            body = ["No wanderers today. Rest a day - word will spread."]
            for l in ui.panel(" NONE ", body, ui.DIM):
                print(l)
            c = ui.choose(":", ["Back"])
            return
        lines = []
        for i, cp in enumerate(pool):
            t = mdata.MONSTERS[cp["species"]]
            cost = naming_sys.name_cost(h, cp["species"])
            lines.append(f"{i+1}. {t['glyph']} {t['name']} Lv{cp['level']}   naming cost {cost} MP")
        for l in ui.panel(" WILLING SOULS ", lines, ui.M):
            print(l)
        ci = ui.choose("Name which one?", [f"{mdata.MONSTERS[c['species']]['name']}" for c in pool], allow_cancel=True)
        if ci is None:
            return
        cp = pool[ci]
        result = naming_sys.naming_ceremony(state, cp["species"], cp["level"])
        if result:
            pool.pop(ci)


def descend(state):
    zone = mdata.ZONES[state["world"]["zone"]]
    cur = state["world"]["floor"]
    if cur >= zone["floors"]:
        print(f"{ui.Y}No deeper path lies here.{ui.RESET}")
        ui.pause()
        return
    state["world"]["floor"] = cur + 1
    deepest = state["world"].setdefault("deepest_floor", 1)
    if state["world"]["floor"] > deepest:
        state["world"]["deepest_floor"] = state["world"]["floor"]
    print(f"You move deeper... Floor {state['world']['floor']}.")
    ui.pause()


def travel(state):
    unlocked = state["world"].get("unlocked_zones", [])
    cur = state["world"]["zone"]
    ids = [cur] + [z for z in unlocked if z != cur]
    opts = []
    for zid in ids:
        marker = "(current) " if zid == cur else ""
        opts.append(f"{marker}{mdata.ZONES[zid]['name']}")
    i = ui.choose("Travel where?", opts, allow_cancel=True)
    if i is None:
        return
    state["world"]["zone"] = ids[i]
    state["world"]["floor"] = 1
    print(f"You set off... {mdata.ZONES[ids[i]]['name']}.")
    print(mdata.ZONES[ids[i]]["desc"])
    ui.pause()


def equip_purchase(state, key):
    h = state["hero"]
    item = idata.ITEMS[key]
    slot = item["slot"]
    stat_key = "atk" if slot == "weapon" else "def"
    cur = h.gear.get(slot)
    if cur and idata.ITEMS[cur].get(stat_key, 0) >= item.get(stat_key, 0):
        print(ui.R + f"You already wield better ({idata.ITEMS[cur]['name']})." + ui.RESET)
        return False
    old = h.gear.get(slot)
    if old:
        refund = idata.ITEMS[old]["value"] // 2
        h.gold += refund
        print(ui.DIM + f"{idata.ITEMS[old]['name']} sold back for {refund}g." + ui.RESET)
    h.gear[slot] = key
    ui.voice(f"Equipment updated: {item['name']} equipped.")
    return True


def shop_menu(state):
    h = state["hero"]
    in_village = state["world"]["zone"] == "goblin_village"
    stock = idata.VILLAGE_SHOP if in_village else idata.SHOP
    title = "VILLAGE STORES" if in_village else "WANDERING MERCHANT"
    while True:
        ui.clear()
        ui.header(title, f"Gold: {ui.GOLD_C}{h.gold}{ui.RESET}")
        opts = []
        for k in stock:
            it = idata.ITEMS[k]
            desc = it.get("desc", "")
            stat = ""
            if it["kind"] == "gear":
                stat = f"+{it.get('atk', it.get('def', 0))} {'ATK' if it['slot']=='weapon' else 'DEF'}"
            owned = f" x{h.consumables[k]}" if it["kind"] == "consumable" and k in h.consumables else ""
            opts.append(f"{it['name']}{owned} - {it['value']}g  {stat}  {ui.DIM}{desc}{ui.RESET}")
        opts.append(f"Sell materials")
        i = ui.choose("Trade:", opts, allow_cancel=True)
        if i is None or i == len(opts) - 1:
            if i == len(opts) - 1:
                gold = 0
                for m, n in list(h.materials.items()):
                    sell = n - 1
                    if sell > 0:
                        gold += idata.ITEMS.get(m, {}).get("value", 0) * sell
                        h.materials[m] = 1
                h.gold += gold
                ui.voice(f"Goods sold. +{gold} gold.")
                continue
            return
        key = stock[i]
        item = idata.ITEMS[key]
        price = item["value"]
        if h.gold < price:
            ui.pause(ui.R + "Not enough gold." + ui.RESET)
            continue
        if item["kind"] == "gear":
            h.gold -= price
            if not equip_purchase(state, key):
                h.gold += price
            ui.pause()
            continue
        h.gold -= price
        h.consumables[key] = h.consumables.get(key, 0) + 1
        print(f"Bought {item['name']}.")
        ui.pause()


def save_and_quit(state):
    from src.core.save import save_game
    persist_world(state)
    payload = {
        "player": state["hero"].to_dict(),
        "world": dict(state["world"]),
        "roster": list(state.get("roster", [])),
        "captures": list(state.get("captures", [])),
    }
    if state.get("kingdom") is not None:
        payload["kingdom"] = state["kingdom"].to_dict()
    if state.get("postgod") is not None:
        payload["postgod"] = dict(state["postgod"])
    ok = save_game(payload, slot=state["world"].get("slot", 1))
    if ok:
        ui.voice("Progress recorded in the Akashic records.")
    ui.pause()


def persist_world(state):
    naming_sys.save_roster(state, naming_sys.load_roster(state))


def hub_loop(state):
    while True:
        h = state["hero"]
        zid = state["world"]["zone"]
        zone = mdata.ZONES[zid]
        ui.clear()
        ep = h.compute_ep()
        loc = f"{zone['name']} B{state['world']['floor']}F" if not zone.get("village") else zone["name"]
        ui.header(f"Day {state['world']['day']} | {loc}",
                  f"{h.name} Lv{h.level} | EP {ep:,} [{rank_from_ep(ep)}]")
        print(f"{ui.DIM}{zone['desc']}{ui.RESET}")
        print()
        hp_bar = ui.bar(h.hp, h.max_hp, 16)
        mp_bar = ui.bar(h.mp, h.max_mp, 12, color=ui.MP_C)
        print(f"  HP {hp_bar}")
        print(f"  MP {mp_bar}")
        party = naming_sys.party_subs(state)
        if party:
            pl = "  ".join(f"{ui.BG}{s.glyph} {s.name} Lv{s.level}{ui.RESET}" for s in party)
            print(f"  Party: {pl}")
        print()

        actions = [
            ("Explore", lambda: explore(state)),
            ("Roster", lambda: naming_sys.roster_menu(state)),
        ]
        caps = state.get("captures", [])
        if caps:
            actions.insert(1, (f"Spared Souls ({len(caps)})", lambda: naming_sys.captures_menu(state)))
        if state.get("kingdom") and zid == "goblin_village":
            actions.append(("Tempest Governance", lambda: kingdom_screen.kingdom_menu(state)))
        actions.append(("Trials & Conquests", lambda: events_sys.trials_menu(state)))
        if h.godhood:
            actions.append(("Celestial Gates", lambda: post_god.gates_menu(state)))
        actions.append(("Descend deeper", lambda: descend(state)))
        if state["world"].get("unlocked_zones"):
            actions.append(("Travel", lambda: travel(state)))
        if zid == "goblin_village":
            actions.append(("Recruit Followers", lambda: recruit_menu(state)))
        actions += [
            ("Rest (full recovery)", lambda: rest(state)),
            ("Character Status", lambda: status_view(state)),
            ("Skills & Mastery", lambda: skills_menu(state)),
            ("Stomach / Materials", lambda: predator_sys.stomach_menu(state)),
            ("Merchant" if not (zid == "goblin_village") else "Village Stores", lambda: shop_menu(state)),
            ("Save Game", lambda: save_and_quit(state)),
            ("Quit to Title", None),
        ]
        labels = [a[0] for a in actions]
        c = ui.choose("What will you do?", labels)
        if c is None or c >= len(actions) - 1:
            save_and_quit(state)
            return
        actions[c][1]()
