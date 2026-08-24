# auto-webified build (async input bridge) - do not edit
import random
from src.core import ui
from src.data import monsters as mdata
from src.data import buildings as bdata
from src.data import items as idata
from src.systems import combat
from src.systems import naming as naming_sys
from src.systems import progression

async def arc_check(state):
    flags = state['world'].setdefault('flags', {})
    w = state['world']
    k = state.get('kingdom')
    if w['phase'] == 1 and k is not None and (not flags.get('orc_war_done')):
        if not flags.get('orc_war_warned') and w['day'] >= 3:
            flags['orc_war_warned'] = True
            flags['orc_war_countdown'] = 2
            print()
            ui.voice(['Warning. A massive migration of starving orcs detected.', 'Estimated arrival: two days.', 'The horde is led by a Disaster-class existence.'])
            k.add_history('Orc horde sighted at the forest border.')
            print(ui.BR + "Scouts: the Orc Lord's horde numbers in the hundreds of thousands..." + ui.RESET)
            await ui.pause()
        elif flags.get('orc_war_warned'):
            flags['orc_war_countdown'] -= 1
            if flags['orc_war_countdown'] <= 0:
                return 'orc_war'
    if w['phase'] >= 4 and (not flags.get('walpurgis_done')):
        return 'walpurgis'
    if flags.get('octagram_done') and (not flags.get('empire_war_done')):
        if not flags.get('empire_warned'):
            flags['empire_warned'] = True
            flags['empire_wave'] = 0
            flags['empire_next'] = 1
            print()
            ui.voice(['Eastern Empire mobilized: 700,000 troops, 2,000 magitanks.', 'Their target: your labyrinth. Their goal: annihilation.', 'Defense waves will strike on consecutive days.'])
            await ui.pause()
        else:
            flags['empire_next'] -= 1
            if flags['empire_next'] <= 0:
                return 'empire_wave'
    return None

async def orc_war_event(state):
    h = state['hero']
    flags = state['world']['flags']
    k = state['kingdom']
    print()
    for l in ui.text_panel(' THE ORC DISASTER ', 'The forest itself flees before them - two hundred thousand starving orcs and their lord, a mountain of hunger wearing a crown of tusks.', ui.R):
        print(l)
    print()
    waves = [(['orc_soldier', 'orc_soldier'], 'The first tide breaks against your lines.'), (['orc_rider', 'orc_soldier'], 'Orc riders crash into the flank!'), (['orc_lord_geld'], 'Geld himself advances, cleaver dragging furrows in the earth.')]
    souls_mult = 3
    for i, (squad, flavor) in enumerate(waves, 1):
        print(f'\n{ui.Y}-- WAVE {i}/3 --{ui.RESET}')
        print(flavor)
        c = await ui.choose('Command:', ['Take the field', 'Let the walls work'])
        scale = 0.9 + i * 0.1
        defense_cut = min(40, int(k.city_defense() / 14))
        enemies = []
        from src.entities.unit import enemy_from_template
        for mid in squad:
            enemies.append(enemy_from_template(mid, scale * (1 - defense_cut / 100.0)))
        power = sum((e.ep_value for e in enemies))
        if c == 0:
            allies = naming_sys.party_subs(state)
            b = combat.Battle(h, allies, enemies, location=f'ORC WAR - Wave {i}')
            b.set_incoming_mult(0.75)
            h.barrier_hp = int(h.max_hp * 0.35)
            result = await b.run()
            win = result['result'] == 'win'
            if win:
                h.kills += len(enemies)
                from src.screens.hub import gain_rewards, revive_party
                gain_rewards(state, {'xp': sum((e.xp_reward for e in enemies)), 'drops': {}})
                revive_party(state)
        else:
            win = k.city_defense() * 60 + h.compute_ep() > power * 1.05
            print('\nYour defenses grind the attackers down...')
        if not win:
            destroyed, plunder, loss = k.siege_damage(random.Random())
            dname = bdata.BUILDINGS[destroyed]['name'] if destroyed else 'the outskirts'
            ui.voice(f'The wave overwhelms the walls. Lost: {dname}, {plunder}g plundered.')
            flags['orc_war_countdown'] = 3
            await ui.pause()
            return False
        gained = progression.gain_souls_from(state, enemies, souls_mult)
        print(f'{ui.M}Souls harvested: +{gained:,} (total {h.souls:,}){ui.RESET}')
        heal_amt = h.max_hp - h.hp
        h.hp = h.max_hp
        h.mp = h.max_mp
        subs_now = naming_sys.party_subs(state)
        for s in subs_now:
            s.hp = s.max_hp
            s.mp = s.max_mp
        naming_sys.save_roster(state, subs_now)
        print(f'{ui.BG}Your forces regroup and fully recover between waves.{ui.RESET}')
        if i == 2:
            h.hp = h.max_hp
            h.mp = h.max_mp
            subs_final = naming_sys.party_subs(state)
            for s in subs_final:
                s.hp = s.max_hp
                s.mp = s.max_mp
                s.barrier_hp = int(s.max_hp * 0.35)
            naming_sys.save_roster(state, subs_final)
            h.barrier_hp = int(h.max_hp * 0.35)
            print(f'{ui.BY}The final wave approaches! Barrier generators shield your party!{ui.RESET}')
    flags['orc_war_done'] = True
    state['world']['phase'] = max(state['world']['phase'], 2)
    geld = mdata.MONSTERS['orc_lord_geld']
    naming_sys.captures_add(state, 'orc_soldier', 8)
    k.treasury += 800
    k.add_history('Repelled the Orc Disaster. The Jura Forest knows its ruler.')
    print()
    ui.voice(['The Orc Disaster has fallen.', f'Confirmed. Souls harvested: {h.souls:,}.', 'Regional threat level: reduced. Your name spreads beyond the forest.'])
    print(ui.GOLD_C + '+800g war spoils. A spared orc soldier awaits naming.' + ui.RESET)
    await ui.pause()
    return True

async def walpurgis_event(state):
    flags = state['world'].setdefault('flags', {})
    h = state['hero']
    print()
    for l in ui.text_panel(' WALPURGIS ', "A ring of black fire drags you into an otherworldly hall. Eight thrones. Seven monsters old enough to remember the world's birth - and one seat, new, waiting for you.", ui.BM):
        print(l)
    print()
    print(f'''{ui.BW}Guy Crimson: "So. The newcomer that devoured Charybdis' kin and broke an empire's toy."''')
    print(f'{ui.BW}Milim Nava: "Boooring talk! Newbie! Fight me sometime!"')
    print(f'{ui.BW}Ramiris: "Your labyrinth sounds SO fun! I approve!"{ui.RESET}')
    print()
    c = await ui.choose('Claim your seat?', ["Accept. I am Rimuru's equal in nothing and my own self entirely - I claim the eighth seat.", 'Stay silent'])
    flags['walpurgis_done'] = True
    flags['octagram_member'] = True
    state['world']['flags']['octagram_done_hint'] = True
    ui.voice(['The Octagram is complete.', 'Demon Lord [' + h.name + '] recognized by the council.', 'Rival trials unlocked: prove yourself to Milim, Leon, and Guy.'])
    k = state.get('kingdom')
    if k:
        k.add_history('Walpurgis: the eighth throne filled.')
    await ui.pause()
TRIALS = [{'id': 'charybdis_hunt', 'name': 'Hunt: Charybdis', 'boss': 'charybdis', 'req_phase': 2, 'repeatable': True, 'desc': 'A calamity-class spirit rampages near the lake. Massive souls await.'}, {'id': 'remnant_hunt', 'name': 'Mop-Up: Orc Remnants', 'boss': None, 'squad': ['orc_soldier', 'orc_rider', 'orc_soldier'], 'req_phase': 2, 'repeatable': True, 'desc': 'Stragglers of the broken horde still pillage the plains. Harvest their souls.'}, {'id': 'milim', 'name': 'Rival Trial: Milim Nava', 'boss': 'milim_trial', 'req_phase': 4, 'req_flag': 'walpurgis_done', 'desc': "The Destroyer wants her 'fun'. Recommended: post-awakening, ultimate skills."}, {'id': 'leon', 'name': 'Rival Trial: Leon Cromwell', 'boss': 'leon_trial', 'req_phase': 4, 'req_flag': 'milim_defeated', 'desc': "The Platinum Devil answers Milim's defeat with interest."}, {'id': 'guy', 'name': 'Rival Trial: Guy Crimson', 'boss': 'guy_trial', 'req_phase': 4, 'req_flag': 'leon_defeated', 'desc': 'The oldest demon lord closes the circle. Survive his scrutiny.'}, {'id': 'kondo', 'name': 'War Duel: Lt. General Kondo', 'boss': 'kondo_guardian', 'req_phase': 5, 'req_flag': 'empire_war_done', 'desc': "The Imperial Guardians' leader demands satisfaction."}, {'id': 'michael', 'name': 'THE ADMINISTRATOR: Michael', 'boss': 'michael_admin', 'req_phase': 6, 'req_flag': 'kondo_defeated', 'ultimate': True, 'desc': 'Only ultimates can pierce his aura. Seize Ultimate Dominion. Become.'}]

async def trials_menu(state):
    flags = state['world'].setdefault('flags', {})
    while True:
        ui.clear()
        ui.header('TRIALS & CONQUESTS', f"Phase {state['world']['phase']} | Souls {state['hero'].souls:,}")
        lines = []
        avail = []
        for t in TRIALS:
            ok = state['world']['phase'] >= t['req_phase']
            if t.get('req_flag') and (not flags.get(t['req_flag'])):
                ok = False
            done_flag = t['id'] + '_defeated'
            status = ''
            if flags.get(done_flag) and (not t.get('repeatable')):
                status = f'{ui.BG}[CLEARED]{ui.RESET}'
            elif t.get('ultimate'):
                status = ui.BY + '[ULTIMATE]' + ui.RESET
            mark = ui.BG if ok else ui.DIM
            boss = mdata.MONSTERS[t['boss']]
            lines.append(f"{mark}{status} {t['name']}{ui.RESET} - {ui.DIM}{t['desc']}{ui.RESET}")
            if ok and (not flags.get(done_flag) or t.get('repeatable')):
                avail.append(t)
        for l in ui.panel(' CHALLENGES ', lines, ui.M):
            print(l)
        opts = [t['name'] for t in avail]
        if not opts:
            await ui.pause('No trials currently available. Enter...')
            return
        i = await ui.choose('Accept which trial?', opts, allow_cancel=True)
        if i is None:
            return
        await run_trial(state, avail[i])
        return

async def run_trial(state, trial):
    h = state['hero']
    from src.entities.unit import enemy_from_template
    scale = max(0.8, 1 + (state['world']['day'] - 20) / 200.0)
    if trial.get('squad'):
        enemies = [enemy_from_template(mid, scale) for mid in trial['squad']]
        boss = None
        title = trial['name'].upper()
    else:
        boss = enemy_from_template(trial['boss'], scale)
        enemies = [boss]
        title = trial['name'].upper()
        print()
        print(f'{ui.ENEMY_C}{boss.glyph} {boss.name}{ui.RESET}')
        print(ui.DIM + (boss.desc or '') + ui.RESET)
    c = await ui.choose('Begin?', ['Fight!', 'Withdraw'])
    if c != 0:
        return
    allies = naming_sys.party_subs(state)
    b = combat.Battle(h, allies, enemies, location=title)
    result = await b.run()
    if result['result'] != 'win':
        print(ui.R + 'Trial failed. Grow stronger.' + ui.RESET)
        await ui.pause()
        return
    h.kills += len(enemies)
    from src.screens.hub import gain_rewards, revive_party, postbattle_souls
    gain_rewards(state, {'xp': sum((e.xp_reward for e in enemies)), 'drops': {}})
    revive_party(state)
    mult = 5 if trial.get('ultimate') else 3 if trial['id'] == 'charybdis_hunt' else 3
    gained = progression.gain_souls_from(state, enemies, mult)
    drops = {}
    for e in enemies:
        for mat, chh in e.drops:
            if random.random() < chh:
                drops[mat] = drops.get(mat, 0) + 1
    for m, n in drops.items():
        h.materials[m] = h.materials.get(m, 0) + n
    if drops:
        dl = ', '.join((f"{idata.ITEMS[m]['name']} x{n}" for m, n in drops.items()))
        print(f'{ui.Y}Spoils: {dl}{ui.RESET}')
    print(f'{ui.M}Souls harvested: +{gained:,} (total {h.souls:,}){ui.RESET}')
    await progression.check_awakening(state)
    flags = state['world'].setdefault('flags', {})
    if boss is not None:
        flags[trial['id'] + '_defeated'] = True
    if trial['id'] == 'guy':
        flags['octagram_done'] = True
        state['world']['phase'] = max(state['world']['phase'], 5)
        ui.voice('All three rivals acknowledged. The Octagram bows to its eighth - and the Empire trembles.')
    if trial['id'] == 'kondo':
        state['world']['phase'] = max(state['world']['phase'], 6)
        ui.voice('The Guardian leader falls. Behind him stands something older than empires...')
    if trial['id'] == 'michael':
        await progression.check_godhood(state)
    await ui.pause()

async def empire_wave_event(state):
    h = state['hero']
    flags = state['world'].setdefault('flags', {})
    k = state['kingdom']
    wave_no = flags.get('empire_wave', 0) + 1
    flags['empire_wave'] = wave_no
    squads = {1: ['imperial_guard', 'mercenary', 'mercenary'], 2: ['imperial_guard', 'imperial_guard'], 3: ['kondo_guardian']}
    squad = squads.get(wave_no, ['imperial_guard', 'imperial_guard'])
    print()
    for l in ui.text_panel(f' EMPIRE INVASION - WAVE {wave_no}', "Magitanks crest the ridge. The Empire's vanguard tests your labyrinth's teeth.", ui.R):
        print(l)
    from src.entities.unit import enemy_from_template
    enemies = [enemy_from_template(mid, 1.0 + wave_no * 0.12) for mid in squad]
    c = await ui.choose('Response:', ['Sortie personally', 'Labyrinth defenses handle it'])
    defense_cut = min(40, int(k.city_defense() / 13))
    power = sum((e.ep_value for e in enemies))
    from src.screens.hub import gain_rewards, revive_party
    if c == 0:
        allies = naming_sys.party_subs(state)
        b = combat.Battle(h, allies, enemies, location=f'EMPIRE WAR W{wave_no}')
        b.set_incoming_mult(0.75)
        result = await b.run()
        win = result['result'] == 'win'
        if win:
            h.kills += len(enemies)
            gain_rewards(state, {'xp': sum((e.xp_reward for e in enemies)), 'drops': {}})
            revive_party(state)
    else:
        win = k.city_defense() * 70 + h.compute_ep() > power * 1.1
        print('\nThe dungeon floors swallow company after company...')
    if not win:
        destroyed, plunder, loss = k.siege_damage(random.Random())
        dname = bdata.BUILDINGS[destroyed]['name'] if destroyed else 'a district'
        ui.voice(f'Wave {wave_no} breaches the gates. Lost: {dname}, {plunder}g.')
        flags['empire_next'] = 2
        await ui.pause()
        return False
    gained = progression.gain_souls_from(state, enemies, 4)
    print(f'{ui.M}Souls harvested: +{gained:,} (total {h.souls:,}){ui.RESET}')
    if wave_no >= 3:
        flags['empire_war_done'] = True
        state['world']['phase'] = max(state['world']['phase'], 5)
        k.treasury += 3000
        k.add_history('The Empire repelled across three waves. The world re-draws its maps.')
        ui.voice('THE EMPIRE WAR IS OVER. Spoils flood the treasury (+3000g). Angels stir in the far heaven.')
    else:
        flags['empire_next'] = 1
        ui.voice(f'Wave {wave_no} repelled. The next comes tomorrow.')
    await ui.pause()
    return True
