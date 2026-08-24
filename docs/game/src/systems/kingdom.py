# auto-webified build (async input bridge) - do not edit
from src.data import buildings as bdata
JOBS = ['farm', 'smith', 'guard', 'builder', 'research', 'service']
JOB_NAMES = {'farm': 'Farming', 'smith': 'Smithing', 'guard': 'Guard Duty', 'builder': 'Construction', 'research': 'Research', 'service': 'Commerce'}

class Kingdom:

    def __init__(self):
        self.treasury = 250
        self.food = 200
        self.happiness = 65
        self.tax_idx = 0
        self.pop = {'goblin': 120}
        self.buildings = {}
        for bid in bdata.DEFAULT_BUILT:
            self.buildings[bid] = {'done': True, 'days_left': 0}
        for bid in bdata.BUILDINGS:
            if bid not in self.buildings:
                self.buildings[bid] = {'done': False, 'days_left': 0}
        self.jobs = {'farm': 35, 'smith': 10, 'guard': 20, 'builder': 15, 'research': 5, 'service': 15}
        self.relations = {fid: cfg['start_rel'] for fid, cfg in bdata.FACTIONS.items()}
        self.routes = []
        self.rp = 0
        self.perks = []
        self.pending_siege = None
        self.envoy_cd = {}
        self.gift_cd = {}
        self.history = []
        self.deepest_floor = 6

    @property
    def tax_rate(self):
        return [0, 10, 20, 30][self.tax_idx]

    @property
    def total_pop(self):
        return sum(self.pop.values())

    def pop_cap(self):
        return sum((bdata.BUILDINGS[bid].get('pop_cap', 0) for bid, s in self.buildings.items() if s['done']))

    def workforce(self):
        return int(self.total_pop * 0.55)

    def has_perk(self, pid):
        return pid in self.perks

    def has(self, bid):
        return self.buildings.get(bid, {}).get('done', False)

    def built_list(self):
        return [bid for bid, s in self.buildings.items() if s['done']]

    def happiness_eq(self):
        eq = 60
        for bid in self.built_list():
            eq += bdata.BUILDINGS[bid].get('happiness_eq', 0)
        crowding = 0
        cap = self.pop_cap()
        if cap > 0 and self.total_pop / max(1, cap) > 0.85:
            crowding = -8
        tax_pen = -(self.tax_rate // 10) * 2
        return max(5, min(95, eq + crowding + tax_pen))

    def food_production(self):
        base = sum((bdata.BUILDINGS[b].get('food_base', 0) for b in self.built_list()))
        mult = 0.6 + self.jobs['farm'] / 100.0 * 0.8
        return base * mult

    def food_consumption(self):
        return self.total_pop * 0.45

    def city_defense(self):
        d = 10
        for bid in self.built_list():
            d += bdata.BUILDINGS[bid].get('defense', 0)
        for p in self.perks:
            perk = next((x for x in bdata.RESEARCH_PERKS if x['id'] == p))
            d += perk.get('defense', 0)
        d += self.workforce() * (self.jobs['guard'] / 100.0) * 0.08
        return int(d)

    def daily_income(self):
        gold_flat = 0
        labyrinth = 0
        for bid in self.built_list():
            b = bdata.BUILDINGS[bid]
            gold_flat += b.get('gold_flat', 0)
            if b.get('labyrinth_income'):
                labyrinth = 20 + self.deepest_floor * 5
        route_income = sum((bdata.TRADE_ROUTES[r]['income'] for r in self.routes))
        labor_tax = self.total_pop * (self.tax_rate / 100.0) * 0.3
        service_mult = 1 + self.jobs['service'] / 100.0 * 0.6
        income_pct = 1.1 if self.has_perk('logistics') else 1.0
        total = (gold_flat + route_income + labyrinth) * service_mult * income_pct + labor_tax
        return int(total)

    def research_gain(self):
        if not self.has('schoolhouse'):
            return 0.0
        mult = 1.6 if self.has('research_lab') else 1.0
        return self.workforce() * (self.jobs['research'] / 100.0) * 0.4 * mult

    def can_build(self, bid):
        b = bdata.BUILDINGS[bid]
        st = self.buildings[bid]
        if st['done']:
            return (False, 'Already built')
        if st['days_left'] > 0:
            return (False, 'Under construction')
        req = b.get('requires')
        if req and (not all((self.has(r) for r in req))):
            names = ', '.join((bdata.BUILDINGS[r]['name'] for r in req))
            return (False, f'Requires {names}')
        if self.treasury < b['cost_gold']:
            return (False, f"Needs {b['cost_gold']}g")
        return (True, '')

    def missing_mats(self, bid, hero):
        b = bdata.BUILDINGS[bid]
        out = []
        for mat, n in b['cost_mats'].items():
            have = hero.materials.get(mat, 0)
            if have < n:
                from src.data.items import ITEMS
                out.append(f"{ITEMS[mat]['name']} {have}/{n}")
        return out

    def start_building(self, bid, hero):
        ok, why = self.can_build(bid)
        if not ok:
            return (False, why)
        missing = self.missing_mats(bid, hero)
        if missing:
            return (False, 'Missing: ' + ', '.join(missing))
        b = bdata.BUILDINGS[bid]
        self.treasury -= b['cost_gold']
        for mat, n in b['cost_mats'].items():
            hero.materials[mat] -= n
            if hero.materials[mat] <= 0:
                del hero.materials[mat]
        speed = 1 + self.jobs['builder'] / 100.0 * 0.5
        days = max(1, round(b['days'] / speed))
        self.buildings[bid]['days_left'] = days
        return (True, f"{b['name']} underway ({days} days)")

    def unlock_route(self, rid):
        route = bdata.TRADE_ROUTES[rid]
        slots = 2 + (1 if self.has('merchant_guild') else 0)
        if len(self.routes) >= slots:
            return (False, 'No free trade route slots (upgrade Merchant Guild Hall).')
        if rid in self.routes:
            return (False, 'Route already established.')
        if self.relations[route['faction']] < route['req_rel']:
            return (False, f"Requires relation {route['req_rel']}.")
        self.routes.append(rid)
        return (True, f"{route['name']} established (+{route['income']}g/day)")

    def add_history(self, msg):
        self.history.insert(0, msg)
        del self.history[12:]

    def daily_tick(self, hero, day):
        events = []
        for bid, st in list(self.buildings.items()):
            if not st['done'] and st['days_left'] > 0:
                st['days_left'] -= 1
                if st['days_left'] <= 0:
                    st['done'] = True
                    name = bdata.BUILDINGS[bid]['name']
                    events.append(('build_done', f'{name} completed!'))
                    self.add_history(f'{name} completed.')
        income = self.daily_income()
        self.treasury += income
        events.append(('income', f'Daily income: {income}g'))
        prod = self.food_production()
        cons = self.food_consumption()
        self.food += prod - cons
        hungry = False
        if self.food < 0:
            self.food = 0
            hungry = True
            self.happiness -= 8
            lost = max(1, int(self.total_pop * 0.01))
            self.apply_pop_loss(lost)
            events.append(('famine', f'FOOD SHORTAGE! {lost} left the settlement.'))
        hipokute_bid = next((b for b in self.built_list() if bdata.BUILDINGS[b].get('daily_material')), None)
        if hipokute_bid:
            mat = bdata.BUILDINGS[hipokute_bid]['daily_material']
            hero.materials[mat] = hero.materials.get(mat, 0) + 1
            events.append(('delivery', f'+1 {mat} from the fields.'))
        eq = self.happiness_eq()
        drift = (eq - self.happiness) * 0.25
        festival_decay = -2 if self.happiness > eq + 12 else 0
        self.happiness += drift + festival_decay
        self.happiness = max(5, min(98, self.happiness))
        if not hungry and self.happiness >= 50:
            headroom = self.pop_cap() - self.total_pop
            if headroom > 0:
                growth = min(headroom, max(1, int(self.total_pop * 0.012 * ((self.happiness - 40) / 60))))
                self.pop['goblin'] = self.pop.get('goblin', 0) + growth
                if growth > 0:
                    events.append(('growth', f'Population +{growth} (now {self.total_pop}).'))
        self.rp += self.research_gain()
        if int(self.research_gain()) > 0:
            events.append(('research', f'+{self.research_gain():.1f} research points.'))
        if hero.has_skill('great_sage') or hero.has_skill('raphael'):
            pass
        for fid in list(self.envoy_cd.keys()):
            self.envoy_cd[fid] -= 1
            if self.envoy_cd[fid] <= 0:
                del self.envoy_cd[fid]
        for fid in list(self.gift_cd.keys()):
            self.gift_cd[fid] -= 1
            if self.gift_cd[fid] <= 0:
                del self.gift_cd[fid]
        if self.pending_siege:
            self.pending_siege['days'] -= 1
            if self.pending_siege['days'] <= 0:
                faction = self.pending_siege['faction']
                events.append(('siege', faction))
                self.pending_siege = None
        return events

    def apply_pop_loss(self, n):
        remaining = n
        for race in sorted(self.pop, key=lambda r: -self.pop[r]):
            take = min(self.pop[race], remaining)
            self.pop[race] -= take
            remaining -= take
            if remaining <= 0:
                break

    def siege_damage(self, rng):
        destroyed = None
        candidates = [b for b in self.built_list() if b not in bdata.DEFAULT_BUILT]
        if candidates:
            destroyed = rng.choice(candidates)
            self.buildings[destroyed] = {'done': False, 'days_left': 0}
        plunder = int(self.treasury * 0.4)
        self.treasury -= plunder
        self.happiness = max(5, self.happiness - 15)
        loss = max(1, int(self.total_pop * 0.05))
        self.apply_pop_loss(loss)
        return (destroyed, plunder, loss)

    def to_dict(self):
        return {'treasury': self.treasury, 'food': int(self.food), 'happiness': round(self.happiness, 1), 'tax_idx': self.tax_idx, 'pop': dict(self.pop), 'buildings': {b: dict(s) for b, s in self.buildings.items()}, 'jobs': dict(self.jobs), 'relations': dict(self.relations), 'routes': list(self.routes), 'rp': int(self.rp), 'perks': list(self.perks), 'pending_siege': dict(self.pending_siege) if self.pending_siege else None, 'envoy_cd': dict(self.envoy_cd), 'gift_cd': dict(self.gift_cd), 'history': list(self.history), 'deepest_floor': self.deepest_floor}

    @classmethod
    def from_dict(cls, d):
        k = cls.__new__(cls)
        k.treasury = d['treasury']
        k.food = d['food']
        k.happiness = d['happiness']
        k.tax_idx = d['tax_idx']
        k.pop = dict(d['pop'])
        k.buildings = {}
        for bid in bdata.BUILDINGS:
            st = d['buildings'].get(bid)
            k.buildings[bid] = dict(st) if st else {'done': False, 'days_left': 0}
        k.jobs = dict(d['jobs'])
        k.relations = dict(d['relations'])
        k.routes = list(d['routes'])
        k.rp = d['rp']
        k.perks = list(d['perks'])
        k.pending_siege = dict(d['pending_siege']) if d.get('pending_siege') else None
        k.envoy_cd = dict(d.get('envoy_cd', {}))
        k.gift_cd = dict(d.get('gift_cd', {}))
        k.history = list(d.get('history', []))
        k.deepest_floor = d.get('deepest_floor', 6)
        return k
