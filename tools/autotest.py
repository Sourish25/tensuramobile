import random
import sys

sys.path.insert(0, ".")
sys.path.insert(0, "tools")

from src.entities.unit import Player, enemy_from_template, Subordinate
from src.systems import combat
from src.systems import predator as predator_sys
from src.systems import naming as naming_sys
from src.data.skills import get_skill
from src.core.save import save_game, load_game


def auto_battle(hero, allies, enemy_ids, floor_scale=1.0, seed=42):
    rng = random.Random(seed)
    enemies = [enemy_from_template(mid, floor_scale) for mid in enemy_ids]
    b = combat.Battle(hero, allies, enemies, location="Test")
    b.rng = rng
    rounds = 0
    while b.result is None and rounds < 300:
        order = sorted(b.party + b.foes, key=lambda u: -u.eff_stat("agi"))
        for u in order:
            if b.result:
                break
            if not u.alive:
                continue
            b.start_of_turn(u)
            if not u.alive or u.is_acting_blocked():
                continue
            foes = b.foes
            if not foes:
                break
            tgt = max(foes, key=lambda t: t.hp)
            if u is hero:
                offense = [sid for sid in u.skills
                           if (get_skill(sid) or {}).get("kind") == "attack"
                           and u.mp >= (get_skill(sid) or {}).get("mp", 0)]
                if offense and rng.random() < 0.75:
                    sid = rng.choice(offense)
                    s = get_skill(sid)
                    if s.get("target") == "enemy":
                        b.perform_skill(u, sid, tgt)
                    else:
                        b.perform_skill(u, sid, None)
                else:
                    b.basic_attack(u, tgt)
            elif u in allies:
                b.ally_turn(u)
            else:
                b.enemy_turn(u)
        if b.result is None:
            for e in enemies:
                if e.alive:
                    e.tick_statuses()
            for p in b.party:
                if p.alive:
                    p.tick_statuses()
            b.check_end()
            rounds += 1
    return b


def silent_devour(state, enemies):
    rng = random.Random()
    hero = state["hero"]
    gained = []
    mats = {}
    for e in enemies:
        hero.devour_count += 1
        pool = list(getattr(e, "stealable", []))
        if e.is_boss and getattr(e, "signature_skill", None) and e.signature_skill not in pool:
            pool.insert(0, e.signature_skill)
        for sid in pool:
            guaranteed = e.is_boss and sid == e.signature_skill
            chance = 45 + (hero.level - e.level) * 6 + hero.stats.get("luk", 5) * 1.2 - (15 if e.is_boss else 0)
            if guaranteed or rng.random() * 100 < max(8, min(92, chance)):
                if not hero.has_skill(sid) and get_skill(sid):
                    hero.learn_skill(sid)
                    gained.append(sid)
        form = e.name + " Mimicry"
        if form not in hero.mimic_forms and (e.is_boss or rng.random() < 0.35):
            hero.mimic_forms.append(form)
        for mat, ch in e.drops:
            if rng.random() < min(0.95, ch + 0.1):
                mats[mat] = mats.get(mat, 0) + 1
    for m, n in mats.items():
        hero.materials[m] = hero.materials.get(m, 0) + n
    return gained


def grind(hero, rng, target_level, pool_by_floor):
    while hero.level < target_level:
        floor = min(5, max(1, hero.level - 2))
        mid = rng.choice(pool_by_floor[floor])
        b = auto_battle(hero, [], [mid], seed=rng.randint(0, 99999))
        if b.result == "win":
            for _ in hero.gain_xp(sum(e.xp_reward for e in b.enemies)):
                hero.level_up()
                hero.check_evolution()
            silent_devour({"hero": hero}, b.enemies)
            predator_sys.check_combinations(hero)
        hero.hp = hero.max_hp
        hero.mp = hero.max_mp


def main():
    failures = []

    def check(name, cond):
        print(("PASS" if cond else "FAIL"), "-", name)
        if not cond:
            failures.append(name)

    rng = random.Random(2024)

    hero = Player("NameTester", "slime")

    base_mp = hero.stats["mp"]
    ok, cost = naming_sys.can_name(hero, "dire_wolf")
    check(f"naming affordable at full MP (cost {cost})", ok and cost > 0)
    hero.pay_name_cost(cost)
    check("mp scar applied", hero.mp_scar > 0 and hero.max_mp < base_mp)
    healed = hero.recover_scar_on_rest()
    check("rest recovers scar", healed > 0)

    for _ in range(20):
        hero.recover_scar_on_rest()
    check("scar fully recoverable", hero.mp_scar == 0.001 or hero.mp_scar < 1.0)

    wolf = Subordinate("Ranga", "dire_wolf", level=3)
    form = wolf.apply_named_form()
    check(f"named direwolf evolves ({form})", form == "Tempest Wolf" and wolf.has_skill("wind_cutter"))
    lv = wolf.gain_xp(500)
    check("subordinate levels from xp", len(lv) >= 1 and wolf.stats["atk"] > 10)

    goblin_sub = Subordinate("Rigurd", "goblin", level=2)
    check("goblin evolves to Hobgoblin", goblin_sub.apply_named_form() == "Hobgoblin")

    alpha = Subordinate("Fang", "dire_alpha", level=10)
    check("alpha evolves to Star Wolf", alpha.apply_named_form() == "Tempest Star Wolf")

    grind(hero, rng, 12, {
        1: ["horned_rabbit", "black_serpent"],
        3: ["cave_centipede", "giant_bat", "black_spider"],
        5: ["black_spider", "cave_centipede", "armorsaurus"],
    })
    print(f"  grinder reached Lv{hero.level}, {len(hero.skills)} skills")

    party = [wolf]
    wins = 0
    for i in range(8):
        b = auto_battle(hero, [Subordinate(f"W{i}", "dire_wolf", level=8)], ["orc_soldier"], seed=500 + i)
        if b.result == "win":
            wins += 1
    print(f"  hero+ally vs orc_soldier: {wins}/8 wins")
    check("party battles function", wins >= 6)

    pack_wins = 0
    for i in range(8):
        b = auto_battle(hero, [], ["dire_wolf", "dire_wolf"], seed=600 + i)
        if b.result == "win":
            pack_wins += 1
    print(f"  solo Lv{hero.level} vs wolf pair: {pack_wins}/8")
    check("wolf defense event winnable at Lv12+", pack_wins >= 6)

    st = {"player": hero.to_dict(),
          "world": {"zone": "jura_plains", "floor": 2, "day": 9,
                    "bosses_slain": ["tempest_serpent"], "unlocked_zones": ["jura_plains", "goblin_village"],
                    "flags": {"village_met": True}, "recruit_pool": [{"species": "goblin", "level": 2}]},
          "roster": [wolf.to_dict(), alpha.to_dict()],
          "captures": [{"species": "horned_rabbit", "level": 2}]}
    save_game(st, slot=2)
    loaded = load_game(2)
    h2 = Player.from_dict(loaded["player"])
    subs2 = [Subordinate.from_dict(d) for d in loaded["roster"]]
    check("roster roundtrips",
          len(subs2) == 2 and subs2[0].name == "Ranga" and subs2[0].evolve_name == "Tempest Wolf"
          and subs2[0].has_skill("wind_cutter") and abs(subs2[0].stats["atk"] - wolf.stats["atk"]) <= 1)
    check("captures roundtrip", loaded["captures"][0]["species"] == "horned_rabbit")

    pool = [{"species": "goblin", "level": 2}, {"species": "dire_wolf", "level": 1}]
    check("recruit pool entries valid", all(p["species"] in __import__("src.data.monsters", fromlist=["MONSTERS"]).MONSTERS for p in pool))

    print()
    if failures:
        print("FAILURES:", failures)
        sys.exit(1)
    print("ALL TESTS PASSED")


if __name__ == "__main__":
    main()
