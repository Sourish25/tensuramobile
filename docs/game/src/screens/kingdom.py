# auto-webified build (async input bridge) - do not edit
from src.core import ui
from src.data import buildings as bdata
from src.data import items as idata
from src.systems.kingdom import JOBS, JOB_NAMES

def overview_lines(state, k):
    from src.entities.unit import rank_from_ep
    h = state['hero']
    lines = [f'Treasury {ui.GOLD_C}{k.treasury:,}g{ui.RESET}   Income ~{ui.GOLD_C}{k.daily_income()}g/day{ui.RESET}   Tax {k.tax_rate}%   Food {int(k.food)} ({k.food_production():.0f}/day vs -{k.food_consumption():.0f})', f'Population {ui.BW}{k.total_pop}{ui.RESET}/{k.pop_cap()}   ' + '   '.join((f'{r.title()}: {n}' for r, n in k.pop.items())), f'Happiness [{ui.bar(int(k.happiness), 100, 16, color=ui.HP_C, show_nums=False)}] {int(k.happiness)}/100   City Defense {ui.C}{k.city_defense()}{ui.RESET}   Research {ui.BC}{int(k.rp)} RP{ui.RESET}']
    routes = ', '.join((bdata.TRADE_ROUTES[r]['name'] for r in k.routes)) or 'none'
    lines.append(f'Trade Routes: {routes}')
    under = [(bdata.BUILDINGS[b]['name'], s['days_left']) for b, s in k.buildings.items() if not s['done'] and s['days_left'] > 0]
    if under:
        lines.append('Construction: ' + ', '.join((f'{n} ({d}d)' for n, d in under)))
    if k.pending_siege:
        f = bdata.FACTIONS[k.pending_siege['faction']]
        lines.append(ui.R + f"!! INVASION WARNING: {f['name']} attacks in {k.pending_siege['days']} days !!" + ui.RESET)
    return lines

async def kingdom_menu(state):
    k = state.get('kingdom')
    if k is None:
        return
    while True:
        ui.clear()
        ui.header('TEMPES GOVERNANCE', f"Day {state['world']['day']}")
        for l in ui.panel(' REALM OVERVIEW ', overview_lines(state, k), ui.Y):
            print(l)
        print()
        c = await ui.choose('Governance:', ['Districts & Construction', 'Workforce Allocation', 'Economy & Taxation', 'Diplomacy', 'Workshops (Crafting)', 'Academy (Research)', 'Chronicle', 'Back'])
        if c == 0:
            await districts_menu(state, k)
        elif c == 1:
            await workforce_menu(state, k)
        elif c == 2:
            await economy_menu(state, k)
        elif c == 3:
            await diplomacy_menu(state, k)
        elif c == 4:
            await crafting_menu(state, k)
        elif c == 5:
            await academy_menu(state, k)
        elif c == 6:
            await chronicle_menu(state, k)
        else:
            return

async def districts_menu(state, k):
    hero = state['hero']
    while True:
        ui.clear()
        ui.header('DISTRICTS & CONSTRUCTION', f'Treasury {ui.GOLD_C}{k.treasury}g{ui.RESET}')
        by_district = {}
        for bid, b in bdata.BUILDINGS.items():
            by_district.setdefault(b['district'], []).append(bid)
        lines = []
        order = ['central', 'residential', 'industrial', 'agriculture', 'commercial', 'labyrinth', 'academy']
        flat = []
        for did in order:
            dist = bdata.DISTRICTS[did]
            lines.append(f"{ui.BY}-- {dist['name']} --{ui.RESET}")
            for bid in by_district[did]:
                b = bdata.BUILDINGS[bid]
                st = k.buildings[bid]
                mark = f'{ui.BG}[BUILT]{ui.RESET}' if st['done'] else f"{ui.Y}[{st['days_left']}d left]{ui.RESET}" if st['days_left'] > 0 else '[--]'
                cost = f"{b['cost_gold']}g " if b['cost_gold'] else ''
                mats = ' '.join((f"{n}x{idata.ITEMS[m]['name'].split()[0]}" for m, n in b['cost_mats'].items()))
                lines.append(f"  {mark} {b['name']:<24} {cost}{mats}  {ui.DIM}{b['effects_text']}{ui.RESET}")
                if not st['done'] and st['days_left'] == 0:
                    flat.append(bid)
            lines.append('')
        for l in ui.panel(' BLUEPRINTS ', lines[:40], ui.C):
            print(l)
        opts = [f"Build: {bdata.BUILDINGS[b]['name']}" for b in flat]
        if not opts:
            await ui.pause('Nothing available to build. Press Enter...')
            return
        i = await ui.choose('Start construction?', opts, allow_cancel=True)
        if i is None:
            return
        bid = flat[i]
        ok, msg = k.start_building(bid, hero)
        color = ui.BG if ok else ui.R
        print(color + msg + ui.RESET)
        await ui.pause()

async def workforce_menu(state, k):
    while True:
        ui.clear()
        wf = k.workforce()
        ui.header('WORKFORCE ALLOCATION', f'{wf} workers of {k.total_pop} pop')
        lines = []
        for j in JOBS:
            pct = k.jobs[j]
            workers = int(wf * pct / 100.0)
            bar = ui.bar(pct, 100, 20, color=ui.BC, show_nums=False)
            effect = ''
            if j == 'farm':
                effect = f'food x{0.6 + pct / 100 * 0.8:.2f}'
            elif j == 'guard':
                effect = f'+{int(wf * pct / 100.0 * 0.08)} def'
            elif j == 'builder':
                effect = f'x{1 + pct / 100 * 0.5:.2f} build speed'
            elif j == 'research':
                effect = f'+{int(k.research_gain())} rp/day'
            elif j == 'service':
                effect = f'income x{1 + pct / 100 * 0.6:.2f}'
            elif j == 'smith':
                effect = 'crafting quality'
            lines.append(f'{JOB_NAMES[j]:<13} [{bar}] {pct:>3}% (~{workers} workers) {effect}')
        total = sum(k.jobs.values())
        lines.append('')
        lines.append(f'Total: {total}% (must equal 100)')
        for l in ui.panel(' LABOR ', lines, ui.B):
            print(l)
        c = await ui.choose('Adjust:', [f'{JOB_NAMES[j]} +/-5%' for j in JOBS] + ['Done'], allow_cancel=False)
        if c == len(JOBS):
            return
        j = JOBS[c]
        d = await ui.choose('Which way?', ['+5%', '-5%'], allow_cancel=True)
        if d is None:
            continue
        other = JOBS[(JOBS.index(j) + 1) % len(JOBS)]
        if d == 0:
            if k.jobs[other] >= 5 and k.jobs[j] <= 95:
                k.jobs[j] += 5
                k.jobs[other] -= 5
        elif k.jobs[j] >= 5 and k.jobs[other] <= 95:
            k.jobs[j] -= 5
            k.jobs[other] += 5

async def economy_menu(state, k):
    while True:
        ui.clear()
        ui.header('ECONOMY & TAXATION', f'Treasury {ui.GOLD_C}{k.treasury:,}g{ui.RESET}')
        income = k.daily_income()
        labor = int(k.total_pop * (k.tax_rate / 100.0) * 0.3)
        trade = sum((bdata.TRADE_ROUTES[r]['income'] for r in k.routes))
        lines = [f'Projected daily income: {ui.GOLD_C}{income}g{ui.RESET}', f'  Commerce+Routes: {trade > 0 and trade or 0}g from routes; labor tax contributes {labor}g', '', f'Tax rate: {ui.BY}{k.tax_rate}%{ui.RESET}   Happiness equilibrium: {int(k.happiness_eq())}', f'Food: {int(k.food)} stored | production {k.food_production():.0f}/day | consumption {k.food_consumption():.0f}/day']
        for l in ui.panel(' LEDGER ', lines, ui.Y):
            print(l)
        c = await ui.choose('Actions:', [f'Set tax rate (current {k.tax_rate}%)', 'View trade routes', 'Back'])
        if c == 0:
            ti = await ui.choose('Tax level:', ['0% (beloved)', '10% (fair)', '20% (heavy)', '30% (crushing)'], allow_cancel=True)
            if ti is not None:
                k.tax_idx = ti
        elif c == 1:
            rl = []
            for rid, r in bdata.TRADE_ROUTES.items():
                status = f"{ui.BG}[ACTIVE +{r['income']}g/d]{ui.RESET}" if rid in k.routes else f"{ui.DIM}[needs {r['req_rel']} rel with {bdata.FACTIONS[r['faction']]['name']}]{ui.RESET}"
                rl.append(f"{r['name']}: {status} {ui.DIM}{r['desc']}{ui.RESET}")
            for l in ui.panel(' TRADE ROUTES ', rl, ui.G):
                print(l)
            await ui.pause()
        else:
            return

async def diplomacy_menu(state, k):
    hero = state['hero']
    while True:
        ui.clear()
        ui.header('DIPLOMACY', 'Nations of the Great Jura and beyond')
        lines = []
        for fid, f in bdata.FACTIONS.items():
            rel = k.relations[fid]
            col = ui.BG if rel >= 30 else ui.Y if rel >= -20 else ui.R
            bar = ui.bar(rel + 100, 200, 18, color=col, show_nums=False)
            route = next((rid for rid, r in bdata.TRADE_ROUTES.items() if r['faction'] == fid), None)
            rt = f"  Route: {('OPEN' if route in k.routes else 'locked')}"
            cd = f' (envoy cd {k.envoy_cd[fid]}d)' if fid in k.envoy_cd else ''
            lines.append(f"{f['color']}{f['name']}{ui.RESET}  rel {rel:+d} [{bar}]")
            lines.append(f"   {ui.DIM}{f['blurb']}{rt}{cd}{ui.RESET}")
        for l in ui.panel(' FOREIGN POWERS ', lines, ui.M):
            print(l)
        opts = []
        fids = list(bdata.FACTIONS.keys())
        sel = await ui.choose('Treat with which power?', [bdata.FACTIONS[f]['name'] for f in fids], allow_cancel=True)
        if sel is None:
            return
        fid = fids[sel]
        f = bdata.FACTIONS[fid]
        envoy_cost = max(10, 50 - (20 if k.has('guest_house') else 0))
        actions = [f'Send Envoy (-{envoy_cost}g)', 'Send Gift (-150g)']
        route_id = next((rid for rid, r in bdata.TRADE_ROUTES.items() if r['faction'] == fid), None)
        if route_id and route_id not in k.routes:
            actions.append(f"Propose Trade Pact ({bdata.TRADE_ROUTES[route_id]['req_rel']}+ rel)")
        actions.append('Back')
        a = await ui.choose(f"{f['name']}:", actions, allow_cancel=False)
        if a == 0:
            if fid in k.envoy_cd:
                print(ui.Y + f'An envoy already departed recently.' + ui.RESET)
            elif k.treasury < envoy_cost:
                print(ui.R + 'Not enough gold.' + ui.RESET)
            else:
                k.treasury -= envoy_cost
                bonus = 2 + (k.has('guest_house') and 2 or 0)
                delta = bonus + hero.stats.get('luk', 5) % 4
                k.relations[fid] = min(100, k.relations[fid] + delta)
                k.envoy_cd[fid] = 3
                ui.voice(f"Your envoy was received by {f['name']}. Relations +{delta}.")
        elif a == 1:
            if fid in k.gift_cd:
                print(ui.Y + 'They received enough gifts lately.' + ui.RESET)
            elif k.treasury < 150:
                print(ui.R + 'Not enough gold.' + ui.RESET)
            else:
                k.treasury -= 150
                delta = 12 + (2 if k.has('guest_house') else 0)
                k.relations[fid] = min(100, k.relations[fid] + delta)
                k.gift_cd[fid] = 5
                ui.voice(f'The gift is well received. Relations +{delta}.')
        elif a == 2 and route_id:
            ok, msg = k.unlock_route(route_id)
            color = ui.BG if ok else ui.R
            print(color + msg + ui.RESET)
            if ok:
                ui.voice(msg)
        await ui.pause()

async def crafting_menu(state, k):
    hero = state['hero']
    if not k.has('forge'):
        for l in ui.text_panel(' NO FORGE ', ["Build Kaijin's Forge in the Industrial District first."], ui.R):
            print(l)
        await ui.pause()
        return
    while True:
        ui.clear()
        ui.header('WORKSHOPS', 'Kaijin hammers away at your behest')
        lines = []
        craftable = []
        for rec in bdata.CRAFT_RECIPES:
            item = idata.ITEMS[rec['id']]
            locked = not all((k.has(r) for r in rec['requires']))
            half = k.has_perk('medicine')
            mats = {m: (n + 1) // 2 if half else n for m, n in rec['mats'].items()}
            can = all((hero.materials.get(m, 0) >= n for m, n in mats.items())) and (not locked)
            lock_tag = ui.R + '[LOCKED]' + ui.RESET if locked else ''
            mat_str = ' '.join((f"{n}x{idata.ITEMS[m]['name'].split()[0]}({hero.materials.get(m, 0)})" for m, n in mats.items()))
            mark = ui.BG + '[READY]' + ui.RESET if can else ui.DIM + '[need mats]' + ui.RESET
            lines.append(f"{mark} {item['name']:<22} {mat_str} {lock_tag}")
            if can:
                craftable.append((rec, mats))
        for l in ui.panel(' RECIPES ', lines, ui.Y):
            print(l)
        if not craftable:
            await ui.pause('Nothing craftable yet. Enter...')
            return
        i = await ui.choose('Craft what?', [idata.ITEMS[r['id']]['name'] for r, _ in craftable], allow_cancel=True)
        if i is None:
            return
        rec, mats = craftable[i]
        for m, n in mats.items():
            hero.materials[m] -= n
            if hero.materials[m] <= 0:
                del hero.materials[m]
        out = rec['id']
        if rec['out_kind'] == 'consumable':
            hero.consumables[out] = hero.consumables.get(out, 0) + 1
        else:
            slot = idata.ITEMS[out]['slot']
            stat_key = 'atk' if slot == 'weapon' else 'def'
            cur = hero.gear.get(slot)
            if cur and idata.ITEMS[cur].get(stat_key, 0) >= idata.ITEMS[out].get(stat_key, 0):
                hero.gold += idata.ITEMS[out]['value'] // 2
                print(ui.DIM + f"Crafted {idata.ITEMS[out]['name']} - sold to the market for {idata.ITEMS[out]['value'] // 2}g." + ui.RESET)
            else:
                hero.gear[slot] = out
                ui.voice(f"[{idata.ITEMS[out]['name']}] has been forged. Equipment updated.")
        print(ui.BG + f"Crafted {idata.ITEMS[out]['name']}!" + ui.RESET)
        await ui.pause()

async def academy_menu(state, k):
    while True:
        ui.clear()
        ui.header('ACADEMY', f'{int(k.rp)} research points banked (+{k.research_gain():.1f}/day)')
        lines = [f"Known perks: {', '.join((p.title() for p in k.perks)) or 'none'}", '']
        avail = []
        for p in bdata.RESEARCH_PERKS:
            if p['id'] in k.perks:
                lines.append(f"{ui.BG}[LEARNED]{ui.RESET} {p['name']} - {p['desc']}")
            else:
                afford = k.rp >= p['rp']
                lines.append(f"{(ui.BG if afford else ui.R)}[{p['rp']} RP]{ui.RESET} {p['name']} - {p['desc']}")
                if afford:
                    avail.append(p)
        for l in ui.panel(' DOCTRINES ', lines, ui.BC):
            print(l)
        if not avail:
            await ui.pause('Nothing to learn right now. Enter...')
            return
        i = await ui.choose('Research which doctrine?', [p['name'] for p in avail], allow_cancel=True)
        if i is None:
            return
        p = avail[i]
        k.rp -= p['rp']
        k.perks.append(p['id'])
        ui.voice(f"Doctrine established: [{p['name']}]. {p['desc']}")

async def chronicle_menu(state, k):
    ui.clear()
    ui.header('CHRONICLE', 'Recent history of the realm')
    lines = k.history[-12:] or ['Nothing of note has happened yet.']
    for l in ui.panel(' RECORDS ', lines, ui.DIM):
        print(l)
    await ui.pause()
