# auto-webified build (async input bridge) - do not edit
import random
from src.core import ui
from src.data import monsters as mdata
from src.data import items as idata
from src.systems import combat
from src.systems import naming as naming_sys
RELICS = [{'id': 'genesis_relic_asura', 'name': 'Asura, Blade of Wrath', 'min_tier': 2}, {'id': 'genesis_relic_ark', 'name': 'Ark, First Sword', 'min_tier': 4}, {'id': 'genesis_relic_crown', 'name': 'Crown of Dawn', 'min_tier': 6}, {'id': 'genesis_relic_mirror', 'name': 'Mirror of Origins', 'min_tier': 8}, {'id': 'genesis_relic_spring', 'name': 'Eternal Spring', 'min_tier': 10}, {'id': 'genesis_relic_compass', 'name': 'Star Compass', 'min_tier': 12}, {'id': 'genesis_relic_grail', 'name': 'Twilight Grail', 'min_tier': 14}]
WORLD_PREFIX = ['The Rust', 'The Silent', 'The Burning', 'The Drowned', 'The Hollow', 'The Gilded', 'Weeping', 'Howling', 'Crystal', 'Endless']
WORLD_SUFFIX = ['Expanse', 'Steppe', 'Ocean', 'Garden', 'Citadel', 'Wastes', 'Archipelago', 'Cathedral', 'Forest', 'Machine']
MODIFIERS = [{'id': 'hardy', 'name': 'Hardy Fauna', 'desc': 'Enemies +40% HP', 'hp': 1.4}, {'id': 'feral', 'name': 'Feral Evolution', 'desc': 'Enemies +30% ATK/MAG', 'atk': 1.3}, {'id': 'rich', 'name': 'Dense Magicules', 'desc': 'Souls x2', 'souls': 2}, {'id': 'opulent', 'name': 'Opulent Ruins', 'desc': 'Essence x1.5', 'essence': 1.5}, {'id': 'brittle', 'name': 'Brittle Existence', 'desc': 'Enemies -25% HP', 'hp': 0.75}, {'id': 'swift', 'name': 'Accelerated Time', 'desc': 'Enemies +25% AGI', 'agi': 1.25}, {'id': 'holy_land', 'name': 'Sanctified Land', 'desc': 'Angelic remnants (+seraphs)', 'pool': 'angel'}, {'id': 'swarm', 'name': 'Swarm Worlds', 'desc': 'Insectoid dominant (+insectors)', 'pool': 'swarm'}]
ESSENCE_UPGRADES = [{'id': 'void_blessing', 'name': 'Blessing of the Void', 'base_cost': 20, 'desc': '+5% to all your stats, permanently.'}, {'id': 'legion_doctrine', 'name': 'Legion Doctrine', 'base_cost': 25, 'desc': "+5% to ALL named subordinates' stats, permanently."}, {'id': 'fate_weaving', 'name': 'Fate Weaving', 'base_cost': 15, 'desc': '+3% crit and dodge, permanently.'}]

def default_postgod():
    return {'gates_cleared': 0, 'essence': 0, 'relics': [], 'authority': 0, 'offers': None, 'upgrade_counts': {}}

def ensure_postgod(state):
    pg = state.get('postgod')
    if pg is None:
        pg = default_postgod()
        state['postgod'] = pg
    return pg

def make_offers(pg):
    tier = pg['gates_cleared'] + 1
    offers = []
    for _ in range(3):
        mods = random.sample(MODIFIERS, 2)
        offers.append({'name': f'{random.choice(WORLD_PREFIX)} {random.choice(WORLD_SUFFIX)}', 'mods': mods, 'tier': tier})
    return offers

def relic_check(state, tier):
    pg = ensure_postgod(state)
    h = state['hero']
    for rel in RELICS:
        if rel['id'] in pg['relics']:
            continue
        if tier >= rel['min_tier']:
            pg['relics'].append(rel['id'])
            h.materials[rel['id']] = h.materials.get(rel['id'], 0) + 1
            for k in h.stats:
                h.stats[k] = int(h.stats[k] * 1.06) + 2
            h.hp = min(h.max_hp, h.stats['hp'])
            ui.voice([f"GENESIS RELIC recovered: [{rel['name']}].", 'Its authority weaves into your existence. All stats permanently increased.', f"Relics: {len(pg['relics'])}/7."])
            if len(pg['relics']) >= 7:
                ui.voice('SEVEN GENESIS RELICS ASSEMBLED. The World Recreator stirs...')
            return
    if tier % 3 == 0:
        pg['essence'] += 10 * tier

async def run_gate(state, offer):
    h = state['hero']
    pg = ensure_postgod(state)
    tier = offer['tier']
    mods = {m['id']: m for m in offer['mods']}
    hp_m = 1.0
    atk_m = 1.0
    agi_m = 1.0
    for m in offer['mods']:
        hp_m *= m.get('hp', 1.0)
        atk_m *= m.get('atk', 1.0)
        agi_m *= m.get('agi', 1.0)
    scale_base = 1.5 * 1.45 ** (tier - 1)
    print()
    for l in ui.text_panel(f" DIMENSIONAL GATE T{tier}: {offer['name'].upper()} ", ' | '.join((m['desc'] for m in offer['mods'])), ui.BY):
        print(l)
    c = await ui.choose('Step through?', ['Enter the world', 'Withdraw'])
    if c != 0:
        return
    pools = {'default': ['cryptid_drone', 'dracobeast'], 'angel': ['seraph_minion', 'cryptid_drone'], 'swarm': ['cryptid_drone', 'insector_warrior']}
    pool_key = next((m.get('pool') for m in offer['mods'] if m.get('pool')), 'default')
    pool = pools[pool_key]
    if tier >= 3:
        pool = list(dict.fromkeys(pool + ['insector_warrior']))
    if tier >= 5:
        pool.append('velgrynd_sc' if tier >= 7 else 'dracobeast')
    for floor in range(1, 4):
        n = 2 if floor < 3 else 3
        enemies = []
        from src.entities.unit import enemy_from_template
        for mid in random.choices(pool, k=n):
            e = enemy_from_template(mid, scale_base * (1 + floor * 0.18))
            e.stats['hp'] = max(1, int(e.stats['hp'] * hp_m))
            e.stats['atk'] = max(1, int(e.stats['atk'] * atk_m))
            e.stats['agi'] = max(1, int(e.stats['agi'] * agi_m))
            e.hp = e.stats['hp']
            enemies.append(e)
        allies = naming_sys.party_subs(state)
        b = combat.Battle(h, allies, enemies, location=f"{offer['name']} - Stratum {floor}")
        result = await b.run()
        if result['result'] != 'win':
            print(ui.R + '\nThe gate expels you, bleeding magicules.' + ui.RESET)
            h.hp = max(1, int(h.max_hp * 0.25))
            await ui.pause()
            return
        h.kills += len(enemies)
        from src.screens.hub import gain_rewards, revive_party
        gain_rewards(state, {'xp': sum((e.xp_reward for e in enemies)) // 2, 'drops': {}})
        revive_party(state)
    boss_id = pick_gate_boss(pg, tier)
    boss = enemy_from_template(boss_id, scale_base * 1.5)
    boss.stats['hp'] = max(1, int(boss.stats['hp'] * hp_m))
    boss.stats['atk'] = max(1, int(boss.stats['atk'] * atk_m))
    boss.hp = boss.stats['hp']
    print(f'\n{ui.ENEMY_C}{boss.glyph} {boss.name}{ui.RESET} - {ui.DIM}{boss.desc}{ui.RESET}')
    b = combat.Battle(h, naming_sys.party_subs(state), [boss], location=f"{offer['name'].upper()} - WORLD HEART")
    result = await b.run()
    if result['result'] != 'win':
        print(ui.R + '\nThe World Heart endures. You are cast out.' + ui.RESET)
        h.hp = max(1, int(h.max_hp * 0.25))
        await ui.pause()
        return
    h.kills += 1
    from src.screens.hub import gain_rewards, revive_party
    gain_rewards(state, {'xp': boss.xp_reward // 2, 'drops': {}})
    revive_party(state)
    gained = progression_gSouls(state, boss, mods)
    essence = int((12 + 6 * tier) * mods.get('opulent', {}).get('essence', 1.0))
    pg['essence'] += essence
    pg['gates_cleared'] += 1
    print()
    ui.voice([f"World heart consumed. [{offer['name']}] folds back into potential.", f'+{gained:,} souls. +{essence} divine essence.'])
    relic_check(state, tier)
    await ui.pause()

def progression_gSouls(state, boss, mods):
    from src.systems.progression import gain_souls_from
    mult = int(mods.get('rich', {}).get('souls', 1))
    return gain_souls_from(state, [boss], max(2, 3 * mult))

def pick_gate_boss(pg, tier):
    t = pg['gates_cleared'] + 1
    if t >= 8:
        return 'feldway_final'
    if t >= 4:
        return 'zeranus_gate'
    if t >= 2:
        return random.choice(['charybdis', 'velgrynd_sc'])
    return random.choice(['charybdis', 'milim_trial'])

async def gates_menu(state):
    pg = ensure_postgod(state)
    while True:
        ui.clear()
        ui.header('CELESTIAL GATES', f"{pg['gates_cleared']} worlds devoured")
        lines = [f"Divine Essence: {ui.BY}{pg['essence']}{ui.RESET}   Relics: {ui.BM}{len(pg['relics'])}/7{ui.RESET}", f"Divine Authority stacks: {ui.GOLD_C}{pg['authority']}{ui.RESET}", '']
        relic_names = [next((r['name'] for r in RELICS if r['id'] == rid)) for rid in pg['relics']]
        lines.append('Relics held: ' + (', '.join(relic_names) if relic_names else ui.DIM + 'none yet' + ui.RESET))
        for l in ui.panel(' THE VOID SEAT ', lines, ui.BY):
            print(l)
        if not pg.get('offers'):
            pg['offers'] = make_offers(pg)
        opts = []
        for i, off in enumerate(pg['offers']):
            mods_txt = ', '.join((m['name'] for m in off['mods']))
            opts.append(f"T{off['tier']} {off['name']}  [{mods_txt}]")
        opts += ['Refresh offers', 'Essence Works', 'World Recreator', 'Back']
        c = await ui.choose('Choose a world:', opts, allow_cancel=False)
        if c is None or c == len(opts) - 1:
            return
        if opts[c].startswith('T') and '  [' in opts[c]:
            await run_gate(state, pg['offers'][c])
            pg['offers'] = None
            continue
        label = opts[c]
        if label.startswith('Refresh'):
            pg['offers'] = None
            continue
        if label == 'Essence Works':
            await essence_menu(state, pg)
            continue
        if label == 'World Recreator':
            await prestige_menu(state, pg)
            continue

async def essence_menu(state, pg):
    while True:
        ui.clear()
        ui.header('ESSENCE WORKS', f"{pg['essence']} divine essence")
        lines = []
        avail = []
        for up in ESSENCE_UPGRADES:
            count = pg['upgrade_counts'].get(up['id'], 0)
            cost = up['base_cost'] + count * 5
            lines.append(f"{ui.BG}[x{count}]{ui.RESET} {up['name']} - {cost} essence {ui.DIM}{up['desc']}{ui.RESET}")
            avail.append((up, cost))
        for l in ui.panel(' PERMANENT BLESSINGS ', lines, ui.BY):
            print(l)
        i = await ui.choose('Purchase which blessing?', [a[0]['name'] for a in avail], allow_cancel=True)
        if i is None:
            return
        up, cost = avail[i]
        if pg['essence'] < cost:
            print(ui.R + 'Not enough essence.' + ui.RESET)
            await ui.pause()
            continue
        pg['essence'] -= cost
        pg['upgrade_counts'][up['id']] = pg['upgrade_counts'].get(up['id'], 0) + 1
        h = state['hero']
        if up['id'] == 'void_blessing':
            for k in h.stats:
                h.stats[k] = int(h.stats[k] * 1.05) + 1
            h.hp = min(h.max_hp, h.stats['hp'])
            ui.voice(f'[{h.name}] grows. All stats +5%, forever.')
        elif up['id'] == 'legion_doctrine':
            from src.entities.unit import Subordinate
            subs = [Subordinate.from_dict(d) for d in state.get('roster', [])]
            for s in subs:
                for k in s.stats:
                    s.stats[k] = int(s.stats[k] * 1.05) + 1
            state['roster'] = [s.to_dict() for s in subs]
            ui.voice('Your legion sharpens. All named followers +5%, forever.')
        else:
            ui.voice('Probability itself learns to favor you.')
        await ui.pause()

async def prestige_menu(state, pg):
    h = state['hero']
    ui.clear()
    ui.header('WORLD RECREATOR', "Azathoth's deepest authority")
    lines = [f"Relics held: {len(pg['relics'])}/7   Authority stacks: {pg['authority']}   Current multiplier: x{2 ** pg['authority']:,}", '', ui.DIM + 'Unmake this world and seed it anew. Your legend, legion, relics,' + ui.RESET, ui.DIM + 'and divinity persist. The world forgets you - and begins again.' + ui.RESET, '', f'Each rebirth: stats DOUBLED (+100%), full restoration,', f'+5000g starting treasury for the new realm.']
    for l in ui.panel(' RECREATE THE WORLD? ', lines, ui.BM):
        print(l)
    if len(pg['relics']) < 3:
        print(ui.R + '\nRequires at least 3 Genesis Relics.' + ui.RESET)
        await ui.pause()
        return
    c = await ui.choose('Unmake creation?', ['Recreate the world (+1 Authority: ALL STATS x2)', 'Not yet'])
    if c != 0:
        return
    pg['authority'] += 1
    for k in h.stats:
        h.stats[k] = int(h.stats[k] * 2)
    h.hp = h.max_hp
    h.mp = h.max_mp
    from src.systems.kingdom import Kingdom
    state['kingdom'] = Kingdom()
    state['kingdom'].treasury += 5000
    w = state['world']
    w['day'] = 1
    w['zone'] = 'celestial_gates'
    w['floor'] = 1
    w['flags'] = {'awakened': True, 'godhood': True, 'michael_defeated': True, 'walpurgis_done': True, 'octagram_done': True, 'empire_war_done': True, 'orc_war_done': True}
    w['unlocked_zones'] = ['sealed_cave', 'jura_plains', 'goblin_village', 'celestial_gates']
    w['bosses_slain'] = []
    w['recruit_pool'] = None
    ui.voice([f"Authority stack {pg['authority']} inscribed.", 'A new world opens its eyes beneath you.', 'The grind, eternal, continues.'])
    await ui.pause()
