# auto-webified build (async input bridge) - do not edit
import random
from src.core import ui
from src.data.skills import get_skill, skill_name, element_mult, RECIPES, COMBO_SKILLS, mastery_rank
from src.data.items import ITEMS

def mastery_gain(unit, sid):
    s = get_skill(sid)
    if not s or s['kind'] == 'passive' or s['tier'] == 'intrinsic':
        return 0
    data = unit.skills.get(sid)
    if not data or data['mastery'] >= 100:
        return 0
    mult = 1.0
    if unit.has_skill('great_sage'):
        mult *= get_skill('great_sage').get('mastery_mult', 2.0)
    if unit.has_skill('raphael'):
        mult = max(mult, get_skill('raphael').get('mastery_mult', 3.0))
    gain = min(100 - data['mastery'], 3 * mult)
    data['mastery'] += gain
    return gain

class BattleLog:

    def __init__(self):
        self.lines = []

    def add(self, line):
        self.lines.append(line)

    def flush(self):
        for ln in self.lines[-14:]:
            print(' ' + ln[:ui.WIDTH - 4])
        self.lines = []

class Battle:

    def __init__(self, hero, allies, enemies, location='Wilds'):
        self.hero = hero
        self.allies = [a for a in allies if a.alive]
        self.enemies = enemies
        self.location = location
        self.round_no = 1
        self.log = BattleLog()
        self.result = None
        self.rng = random.Random()
        self.mastery_snapshot = {sid: d['mastery'] for sid, d in hero.skills.items()}
        self.incoming_mult = 1.0

    def set_incoming_mult(self, mult):
        self.incoming_mult = mult

    @property
    def party(self):
        return [self.hero] + [a for a in self.allies if a.alive]

    @property
    def foes(self):
        return [e for e in self.enemies if e.alive]

    def party_has_ultimate(self):
        for u in self.party:
            for sid in u.skills:
                s = get_skill(sid)
                if s and s['tier'] == 'ultimate' and (s.get('kind') == 'passive'):
                    return True
        return False

    def foes_have_ultimate(self):
        return any((getattr(e, 'gimmicks', {}).get('ultimate_aura') for e in self.enemies if e.alive))

    def party_has_ultimate_passive(self):
        return self.party_has_ultimate()

    async def run(self):
        while self.result is None:
            if self.round_no > 60:
                self.log.add(f'{ui.R}After 60 rounds of stalemate, exhaustion claims your side...{ui.RESET}')
                self.result = 'lose'
                break
            order = sorted(self.party + self.foes, key=lambda u: (-(u.eff_stat('agi') + self.rng.randint(0, 4)), -u.eff_stat('agi')))
            if any((u.has_skill('hunter_instinct') for u in self.party)) and self.round_no == 1:
                hunters = [u for u in self.party if u.has_skill('hunter_instinct')]
                others = [u for u in order if u not in hunters]
                order = hunters + others
            self.draw()
            for u in order:
                if self.result:
                    break
                if not u.alive:
                    continue
                self.start_of_turn(u)
                if not u.alive:
                    continue
                if u.is_acting_blocked():
                    reason = 'stunned' if 'stun' in u.status else 'paralyzed'
                    self.log.add(f'{ui.DIM}{u.name} is {reason} and cannot act!{ui.RESET}')
                    self.draw()
                    continue
                if u is self.hero:
                    await self.player_turn(u)
                elif u in self.allies:
                    self.ally_turn(u)
                else:
                    self.enemy_turn(u)
                self.check_end()
            if self.result is None:
                for e in self.enemies:
                    if e.alive:
                        self.apply_regen(e)
                        e.tick_statuses()
                        self.check_phases(e)
                for p in self.party:
                    if p.alive:
                        p.tick_statuses()
                self.check_end()
                self.round_no += 1
        self.draw(final=True)
        return self.finish()

    def apply_regen(self, e):
        g = getattr(e, 'gimmicks', {})
        rp = g.get('regen_pct', 0)
        if not rp or not e.alive:
            return
        blocked = any((s in e.status for s in g.get('regen_blockers', ['burn'])))
        if blocked:
            if getattr(e, '_regen_warned', False) is False:
                self.log.add(f"{ui.BG}The flames sear {e.name}'s flesh - regeneration stifled!{ui.RESET}")
                e._regen_warned = True
            return
        heal = int(e.max_hp * rp)
        e.hp = min(e.max_hp, e.hp + heal)
        self.log.add(f'{ui.BR}{e.name} knits its wounds back together (+{heal}).{ui.RESET}')

    def check_phases(self, e):
        phases = getattr(e, 'phase_data', None)
        if not phases or not e.alive:
            return
        idx = getattr(e, 'phase_idx', 0)
        while idx < len(phases):
            ph = phases[idx]
            trigger = ph.get('at_hp_pct', 0.5)
            if e.hp / max(1, e.max_hp) <= trigger * (1 + 0.001):
                for sid in ph.get('gain_skills', []):
                    e.learn_skill(sid)
                mults = ph.get('stat_mult', {})
                old_max = e.max_hp
                for k, m in mults.items():
                    e.stats[k] = int(e.stats[k] * m)
                ratio = e.hp / max(1, old_max)
                e.hp = max(1, int(e.max_hp * min(1.0, ratio)))
                bf = ph.get('barrier_field')
                if bf:
                    e.barrier_field_hp = int(bf * (1 + getattr(e, 'phase_idx', 0)))
                summons = ph.get('summon')
                if summons:
                    from src.entities.unit import enemy_from_template
                    scale = getattr(e, 'spawn_scale', 1.0)
                    for mid in summons:
                        minion = enemy_from_template(mid, scale)
                        minion.gimmicks = {}
                        self.enemies.append(minion)
                        self.log.add(f'{ui.ENEMY_C}{minion.name} answers the call!{ui.RESET}')
                msg = ph.get('announce', f'{e.name} transforms!')
                self.log.add(f'{ui.BR}{ui.BOLD}{msg}{ui.RESET}')
                e.phase_idx = idx + 1
                idx += 1
            else:
                break

    def start_of_turn(self, u):
        u.guarding = False
        if getattr(u, 'form_cooldown', 0) > 0:
            u.form_cooldown -= 1
        if u.has_skill('belzebuth') or u.has_skill('azathoth'):
            regen = max(2, int(u.max_mp * 0.03))
            if u.mp < u.max_mp:
                u.mp = min(u.max_mp, u.mp + regen)
        before = u.hp
        expired = u.tick_statuses()
        dmg = before - u.hp
        if dmg > 0:
            src = 'burned' if 'burn' in u.status else 'poisoned' if 'poison' in u.status else 'bleeding'
            self.log.add(f'{ui.BR}{u.name} takes {dmg} damage from being {src}.{ui.RESET}')
        for sname in expired:
            self.log.add(f'{ui.DIM}{u.name} recovers from {sname}.{ui.RESET}')

    def check_end(self):
        if all((not e.alive for e in self.enemies)):
            self.result = 'win'
        elif not self.hero.alive:
            self.result = 'lose'
        elif not any((a.alive for a in self.allies)) and (not self.hero.alive):
            self.result = 'lose'

    def draw(self, final=False):
        from src.core import webbridge
        if webbridge.WEB:
            import json as _json
            foes = []
            for i, e in enumerate(self.enemies, 1):
                foes.append({'idx': i, 'name': e.name, 'glyph': getattr(e, 'glyph', '?'), 'hp': max(0, int(e.hp)), 'max_hp': max(1, int(e.max_hp)), 'alive': bool(e.alive), 'boss': bool(getattr(e, 'is_boss', False)), 'status': ' '.join((k.upper() for k in getattr(e, 'status', {})))})
            party = []
            for u, is_hero in [(self.hero, True)] + [(a, False) for a in self.allies]:
                party.append({'name': u.name, 'glyph': getattr(u, 'glyph', '?'), 'hp': max(0, int(u.hp)), 'max_hp': max(1, int(u.max_hp)), 'mp': max(0, int(u.mp)), 'max_mp': max(1, int(u.max_mp)), 'alive': bool(u.alive), 'hero': bool(is_hero)})
            webbridge.push_battle(_json.dumps({'round': int(self.round_no), 'location': self.location, 'foes': foes, 'party': party, 'final': bool(final)}))
            if final:
                self.log.flush()
            else:
                shown = self.log.lines[-5:]
                for ln in shown:
                    print(' ' + ln[:ui.WIDTH - 4])
                print()
            return
        ui.clear()
        ui.header(f'{self.location} - Round {self.round_no}', f'{len(self.foes)} enemies')
        foe_lines = []
        from src.entities.unit import rank_from_ep
        for i, e in enumerate(self.enemies, 1):
            tag = ' BOSS' if e.is_boss else ''
            state = '' if e.alive else ' (slain)'
            hp_bar = ui.bar(e.hp, e.max_hp, 20, color=ui.ENEMY_C, show_nums=False)
            st = ' '.join((k.upper() for k in e.status))
            tags = ''
            if getattr(e, 'gimmicks', {}).get('ultimate_aura'):
                tags += ui.BY + '[ULTIMATE]' + ui.RESET + ' '
            if getattr(e, 'barrier_field_hp', 0) > 0:
                tags += ui.BM + f'[DOMAIN {e.barrier_field_hp}]' + ui.RESET + ' '
            if getattr(e, 'gimmicks', {}).get('spell_suppress') and e.alive:
                tags += ui.BR + '[SPELL-NULL FIELD]' + ui.RESET + ' '
            if getattr(e, 'phase_data', None) and getattr(e, 'phase_idx', 0) < len(e.phase_data):
                tags += ui.DIM + '[PHASED]' + ui.RESET
            rank = rank_from_ep(int(e.ep_value * (1 + (self.round_no - 1) * 0)))
            foe_lines.append(f'[{i}] {e.glyph} {e.name}{tag}{state} {tags}')
            foe_lines.append(f'      {hp_bar} {e.hp}/{e.max_hp}   {ui.DIM}EP ~{e.ep_value:,} [{rank}]{ui.RESET}')
            if st:
                foe_lines.append(f'      {ui.DIM}{st}{ui.RESET}')
        for l in ui.panel(' ENEMIES ', foe_lines, ui.ENEMY_C):
            print(l)
        print()
        party_lines = []
        units = [(self.hero, True)] + [(a, False) for a in self.allies]
        for u, is_hero in units:
            state = '' if u.alive else ' (down)'
            hp_bar = ui.bar(u.hp, u.max_hp, 18, color=ui.HP_C, show_nums=False)
            mp_bar = ui.bar(u.mp, u.max_mp, 10, color=ui.MP_C, show_nums=False)
            g = ''
            if u.guarding:
                g = '[GUARD] '
            if u.barrier_hp > 0:
                g += f'[BARRIER {u.barrier_hp}] '
            label = '* ' if is_hero else '  '
            form = getattr(u, 'evolve_name', None)
            stage = form or getattr(u, 'stage_name', 'Ally')
            extra = ''
            if is_hero:
                if getattr(u, 'auto', False):
                    extra += ui.BY + '[AUTO] ' + ui.RESET
                if getattr(u, 'active_form', None):
                    extra += ui.BM + f'[{u.active_form}] ' + ui.RESET
                elif u.mimic_forms:
                    extra += ui.DIM + '[forms available] ' + ui.RESET
            party_lines.append(f'{label}{u.name} ({stage}){state} {extra}{g}')
            party_lines.append(f'     HP {hp_bar}  MP {mp_bar} {u.mp}/{u.max_mp}')
        for l in ui.panel(' PARTY ', party_lines, ui.G):
            print(l)
        print()
        if final:
            self.log.flush()
        else:
            shown = self.log.lines[-5:]
            for ln in shown:
                print(' ' + ln[:ui.WIDTH - 4])
            print()

    async def pick_target(self, actor, targets, allow_back=True):
        opts = []
        for t in targets:
            opts.append(f'{t.name}  ({t.hp}/{t.max_hp})')
        idx = await ui.choose('Target?', opts, allow_cancel=allow_back)
        if idx is None:
            return None
        return targets[idx]

    def calc_damage(self, attacker, skill, target, sid=None):
        scale_key = {'atk': 'atk', 'mag': 'mag', 'agi': 'agi'}.get(skill.get('scale'), 'atk')
        atk_stat = attacker.eff_stat(scale_key)
        if attacker is self.hero and skill.get('scale') == 'atk':
            atk_stat += self.hero.weapon_atk()
        mastery = attacker.skills[sid]['mastery'] if sid and sid in attacker.skills else 0
        mast_mult = 1 + mastery / 160.0
        base = skill.get('power', 8) * atk_stat / 11.0 * mast_mult
        phys_pct = 1.0
        if attacker.has_skill('tyrant_edge'):
            phys_pct += get_skill('tyrant_edge').get('phys_pct', 0.12)
        base *= phys_pct
        rage = 1.0
        if attacker.has_skill('berserker'):
            frac = attacker.hp / max(1, attacker.max_hp)
            if frac < 0.3:
                rage += 0.5 * (1 - frac / 0.3)
        base *= rage
        el = skill.get('element', 'physical')
        emult = element_mult(el, target.element) if target.element else 1.0
        if el != 'physical':
            defense = target.eff_stat('spr')
        else:
            defense = target.eff_stat('def')
        reduction = defense * 0.45
        dmg = base * emult - reduction
        dmg *= self.rng.uniform(0.9, 1.1)
        crit_ch = 5
        if attacker.has_skill('tyrant_edge'):
            crit_ch += get_skill('tyrant_edge').get('crit_bonus', 20)
        if attacker.has_skill('sense_heat'):
            crit_ch += get_skill('sense_heat').get('crit_bonus', 3)
        crit = self.rng.randint(1, 100) <= crit_ch
        if crit:
            dmg *= 1.65
        if target.guarding:
            dmg *= 0.45
        g = getattr(target, 'gimmicks', {})
        if g.get('ultimate_aura'):
            tier = get_skill(sid)['tier'] if sid and get_skill(sid) else 'common'
            if tier != 'ultimate':
                dmg *= 0.35
            elif not self.party_has_ultimate():
                dmg *= 0.7
        if el != 'physical' and (not skill.get('pierce_barrier', False)):
            for e in self.enemies:
                if e.alive and getattr(e, 'gimmicks', {}).get('spell_suppress'):
                    dmg *= 0.12
                    break
        if attacker in self.party:
            for e in self.enemies:
                if e.alive and e.has_skill('magic_interference_f'):
                    dmg *= 0.5
                    break
        else:
            for p in self.party:
                if p.alive and p.has_skill('magic_interference_f'):
                    dmg *= 0.5
                    break
        if target.has_skill('susano_oh') and (get_skill(sid)['tier'] if sid and get_skill(sid) else 'common') != 'ultimate':
            dmg *= 1 - get_skill('susano_oh').get('dmg_reduction', 0.25)
        if target is self.hero or target in self.allies:
            dmg *= getattr(self, 'incoming_mult', 1.0)
        dmg = max(1, int(dmg))
        return (dmg, crit, emult, el)

    def apply_hit(self, attacker, skill, target, dmg):
        el = skill.get('element', 'physical')
        is_magic = el != 'physical'
        pierces = skill.get('pierce_barrier', False)
        note = ''
        field = getattr(target, 'barrier_field_hp', 0)
        if field > 0 and is_magic and (not pierces):
            absorbed = min(field, dmg)
            target.barrier_field_hp -= absorbed
            note = f' Domain absorbs {absorbed}.'
            if target.barrier_field_hp <= 0:
                note += ' The domain shatters!'
            return note
        target.hp -= dmg
        if (target is self.hero or target in self.allies) and (not target.alive) and (not getattr(target, '_mercy_used', False)):
            target._mercy_used = True
            target.hp = 1
            return f" {target.name} braces at death's door - and endures at 1 HP!"
        if target.barrier_hp > 0:
            absorbed = min(target.barrier_hp, dmg)
            target.barrier_hp -= absorbed
            target.hp += absorbed
            note += f' Barrier absorbs {absorbed}.'
            if target.barrier_hp <= 0:
                note += ' Barrier shatters!'
        if not target.alive and target.has_skill('parallel_existence') and (not getattr(target, '_pe_used', False)):
            target._pe_used = True
            target.hp = 1
            return f' {target.name} splits a parallel body and refuses to fall!'
        if target.has_skill('jibril_reflect') or 'judgment' in target.status:
            back = int(dmg * 0.4)
            attacker.hp -= max(1, back)
            note += f' Divine Judgment reflects {back}!'
            if not attacker.alive:
                self.log.add(f'{ui.BOLD}{attacker.name} is destroyed by reflected judgment!{ui.RESET}')
        drain = skill.get('drain', 0)
        if drain:
            healed = int(dmg * drain)
            attacker.hp = min(attacker.max_hp, attacker.hp + healed)
            note += f' Drains {healed} HP.'
        for st, ch in (skill.get('status') or {}).items():
            if self.rng.random() < ch:
                target.add_status(st)
                note += f' {target.name}: {st.upper()}!'
        return note

    def perform_skill(self, actor, sid, target):
        skill = get_skill(sid)
        cost = skill.get('mp', 0)
        if actor.mp < cost:
            self.log.add(f"{ui.R}{actor.name} lacks magicules for {skill['name']}.{ui.RESET}")
            return
        actor.mp -= cost
        kind = skill.get('kind')
        if kind == 'support':
            heal_pool = [t for t in ([target] if target else []) if t and t.alive]
            scale_key = {'atk': 'atk', 'mag': 'mag', 'agi': 'agi'}.get(skill.get('scale'), 'mag')
            mastery = actor.skills[sid]['mastery'] if sid in actor.skills else 0
            amount = int(skill.get('power', 0) * max(1, actor.eff_stat(scale_key)) / 9.0 * (1 + mastery / 150.0))
            for t in heal_pool:
                healed = t.max_hp - t.hp
                t.hp = min(t.max_hp, t.hp + amount)
                for st in skill.get('status') or {}:
                    t.add_status(st, 3)
                self.log.add(f"{ui.BG}{actor.name} channels {skill['name']} -> {t.name}: +{min(amount, healed)} HP.{ui.RESET}")
            mastery_gain(actor, sid)
            return
        if kind == 'defense':
            pool = [t for t in ([target] if target else []) if t and t.alive]
            shield = int(skill.get('power', 10) * 2 + actor.eff_stat('mag') / 3)
            for t in pool:
                t.barrier_hp += shield
                self.log.add(f"{ui.C}{actor.name} raises {skill['name']} around {t.name}: Barrier {shield}.{ui.RESET}")
            mastery_gain(actor, sid)
            return
        targets = []
        tmode = skill.get('target', 'enemy')
        if tmode == 'enemy':
            targets = [target]
        elif tmode == 'all_enemies':
            targets = self.foes if actor in self.party else self.party
        elif tmode == 'ally':
            targets = [target]
        elif tmode == 'single_strongest':
            pool = self.foes if actor in self.party else self.party
            targets = [max(pool, key=lambda t: t.max_hp)] if pool else []
        hits = skill.get('hits', 1)
        total = 0
        color = ui.ALLY_C if actor in self.party else ui.ENEMY_C
        exec_thr = skill.get('execute_below', 0)
        for t in targets:
            if not t.alive:
                continue
            for h in range(hits):
                if not t.alive:
                    break
                if exec_thr and t.hp / max(1, t.max_hp) <= exec_thr:
                    consumed = max(1, int(t.max_hp * 0.5))
                    t.hp = 0
                    actor.hp = min(actor.max_hp, actor.hp + int(consumed * 0.6))
                    color2 = ui.ALLY_C if actor in self.party else ui.ENEMY_C
                    self.log.add(f'{color2}{actor.name} CONSUMES {t.name} body and soul! (+{int(consumed * 0.6)} HP){ui.RESET}')
                    mastery_gain(actor, sid)
                    if not t.alive:
                        self.log.add(f'{ui.BOLD}{t.name} exists no more.{ui.RESET}')
                    break
                dmg, crit, emult, el = self.calc_damage(actor, skill, t, sid=sid)
                t.hp -= dmg
                total += dmg
                note = self.apply_hit(actor, skill, t, dmg)
                cmult = f' x{emult:.1f}' if emult != 1.0 else ''
                cc = ' CRIT!' if crit else ''
                verb = 'casts' if skill.get('element', 'physical') != 'physical' else 'uses'
                self.log.add(f"{color}{actor.name} {verb} {skill['name']} -> {t.name}: {dmg} dmg{cmult}{cc}.{note}{ui.RESET}")
                if not t.alive:
                    self.log.add(f'{ui.BOLD}{t.name} is destroyed!{ui.RESET}')
        mastery_gain(actor, sid)
        self.check_end()

    def basic_attack(self, actor, target):
        pseudo = {'id': '_basic', 'name': 'Strike', 'tier': 'common', 'kind': 'attack', 'element': 'physical', 'scale': 'atk', 'power': 9, 'mp': 0, 'hits': 1, 'target': 'enemy'}
        dmg, crit, emult, el = self.calc_damage(actor, pseudo, target)
        t = target
        t.hp -= dmg
        if actor.has_skill('ravenous'):
            steal = max(1, int(dmg * get_skill('ravenous').get('lifesteal_basic', 0.2)))
            actor.hp = min(actor.max_hp, actor.hp + steal)
        note = self.apply_hit(actor, pseudo, t, dmg)
        color = ui.ALLY_C if actor in self.party else ui.ENEMY_C
        cc = ' CRIT!' if crit else ''
        self.log.add(f'{color}{actor.name} strikes {t.name}: {dmg} dmg.{note}{cc}{ui.RESET}')
        if not t.alive:
            self.log.add(f'{ui.BOLD}{t.name} is destroyed!{ui.RESET}')
        self.check_end()
    AUTO_PRIORITY = ['soul consume', 'void collapse', 'hellflare', 'white flare', 'melt slash', 'death march', 'creations blade', 'cardinal', 'sticky steel', 'steel thread', 'time stop', 'flame breath', 'wind cutter', 'water blade', 'lightning bolt', 'fireball', 'icicle lance', 'stone bullet', 'drain', 'ultrasonic']

    def auto_decide(self, u):
        foes = self.foes
        if not foes:
            return ('wait', None)
        if u.hp < u.max_hp * 0.35:
            pot = next((k for k in sorted(u.consumables) if ITEMS.get(k, {}).get('heal_hp')), None)
            if pot and u.consumables.get(pot, 0) > 0:
                return ('item', pot)
        best = (None, -1.0)
        for sid, d in u.skills.items():
            s = get_skill(sid)
            if not s or s.get('kind') != 'attack' or u.mp < s.get('mp', 0):
                continue
            name = s['name'].lower()
            prio = next((i for i, h in enumerate(self.AUTO_PRIORITY) if h in name), 90)
            score = 100 - prio + s.get('power', 5) / 10.0
            if score > best[1]:
                best = (sid, score)
        if best[0]:
            s = get_skill(best[0])
            tgt = max(foes, key=lambda t: t.hp / max(1, t.max_hp)) if s.get('target') == 'enemy' else None
            if s.get('target') == 'enemy':
                tgt = min(foes, key=lambda t: t.hp)
            return ('skill', (best[0], tgt))
        return ('attack', min(foes, key=lambda t: t.hp))

    def run_auto_turn(self, u):
        act, payload = self.auto_decide(u)
        if act == 'item':
            self.use_item(u, payload)
        elif act == 'skill':
            sid, tgt = payload
            if tgt is None:
                tgt = max(self.foes, key=lambda t: t.max_hp) if get_skill(sid).get('target') == 'single_strongest' else None
            self.perform_skill(u, sid, tgt)
        elif act == 'attack':
            self.basic_attack(u, payload)
        else:
            u.guarding = True

    async def player_turn(self, u):
        while True:
            if getattr(u, 'auto', False):
                self.draw()
                c = await ui.choose(f'{u.name} [AUTO] engaged:', ['Keep auto - act on instinct', 'Take control (Auto: OFF)'], allow_cancel=False)
                if c == 1:
                    u.auto = False
                    self.log.add(f'{u.name}: auto-battle released.')
                    continue
                tag = ui.BY + '[AUTO]' + ui.RESET + ' '
                self.log.add(f'{tag}{u.name} acts on instinct...')
                self.run_auto_turn(u)
                return
            self.draw()
            acts = ['Attack', 'Skill', 'Guard', 'Item']
            label_auto = 'Auto: OFF' if not getattr(u, 'auto', False) else 'Auto: ON'
            acts.insert(0, label_auto)
            idx_shift = 1
            if u.mimic_forms:
                acts.append('Form')
            acts.append('Flee')
            c = await ui.choose(f"{u.name}'s turn - command:", acts, allow_cancel=False)
            if c == 0:
                u.auto = not getattr(u, 'auto', False)
                state_txt = ui.BY + 'ENGAGED' + ui.RESET if u.auto else ui.DIM + 'released' + ui.RESET
                self.log.add(f'{u.name}: auto-battle {state_txt}.')
                if u.auto:
                    self.run_auto_turn(u)
                    return
                continue
            elif c == 1:
                tgt = await self.pick_target(u, self.foes, allow_back=True)
                if tgt is None:
                    continue
                self.basic_attack(u, tgt)
                return
            elif c == 2:
                usable = [sid for sid, d in u.skills.items() if (get_skill(sid) or {}).get('kind') in ('attack', 'support', 'defense')]
                names = []
                for sid in usable:
                    s = get_skill(sid)
                    m = u.skills[sid]['mastery']
                    names.append(f"{s['name']} [{s['tier']}] MP:{s.get('mp', 0)} {m:.0f}% ({mastery_rank(m)})")
                si = await ui.choose('Use which skill?', names, allow_cancel=True)
                if si is None:
                    continue
                sid = usable[si]
                s = get_skill(sid)
                if u.mp < s.get('mp', 0):
                    await ui.pause(ui.R + 'Not enough MP. Pick again.' + ui.RESET)
                    continue
                tgt = None
                if s.get('target') == 'enemy':
                    pool = self.foes
                    if len(pool) > 1:
                        tgt = await self.pick_target(u, pool)
                        if tgt is None:
                            continue
                    else:
                        tgt = pool[0]
                elif s.get('target') == 'ally':
                    pool = [x for x in self.party if x.alive]
                    if len(pool) > 1:
                        tgt = await self.pick_target(u, pool)
                        if tgt is None:
                            continue
                    else:
                        tgt = pool[0]
                self.perform_skill(u, sid, tgt)
                return
            elif c == 3:
                u.guarding = True
                self.log.add(f'{ui.C}{u.name} guards.{ui.RESET}')
                return
            elif c == 4:
                keys = [k for k, v in u.consumables.items() if v > 0]
                if not keys:
                    await ui.pause(ui.R + 'No items.' + ui.RESET)
                    continue
                names = [f"{ITEMS[k]['name']} x{u.consumables[k]}" for k in keys]
                ii = await ui.choose('Use which item?', names, allow_cancel=True)
                if ii is None:
                    continue
                k = keys[ii]
                self.use_item(u, k)
                return
            elif c == 5 and 'Form' in acts:
                if getattr(u, 'form_cooldown', 0) > 0 and u.active_form:
                    await ui.pause(ui.R + f'Body still stabilizing ({u.form_cooldown} turns).' + ui.RESET)
                    continue
                fopts = list(u.mimic_forms)
                if u.active_form:
                    fopts.append('Revert to base form')
                fi = await ui.choose('Assume which form?', fopts, allow_cancel=True)
                if fi is None:
                    continue
                if fi == len(fopts) - 1 and u.active_form:
                    u.active_form = None
                    self.log.add(f'{ui.BM}{u.name} flows back to base form.{ui.RESET}')
                    return
                u.active_form = u.mimic_forms[fi]
                u.form_cooldown = 3
                self.log.add(f'{ui.BM}{u.name} shifts form: {u.active_form}! (+15% ATK/DEF/MAG){ui.RESET}')
                return
            elif c == len(acts) - 1:
                agi_u = u.eff_stat('agi')
                avg_foe = sum((e.eff_stat('agi') for e in self.foes)) // max(1, len(self.foes))
                ch = 40 + (agi_u - avg_foe) * 3
                if self.rng.randint(1, 100) <= max(15, min(90, ch)):
                    self.result = 'flee'
                    return
                self.log.add(f'{ui.R}Could not escape!{ui.RESET}')
                return

    def use_item(self, user, key):
        item = ITEMS[key]
        user.consumables[key] -= 1
        if user.consumables[key] <= 0:
            del user.consumables[key]
        if item.get('heal_hp'):
            amt = min(item['heal_hp'], user.max_hp - user.hp)
            user.hp += amt
            self.log.add(f"{ui.BG}{user.name} uses {item['name']}: +{amt} HP.{ui.RESET}")
        if item.get('heal_mp'):
            amt = min(item['heal_mp'], user.max_mp - user.mp)
            user.mp += amt
            self.log.add(f"{ui.BB}{user.name} uses {item['name']}: +{amt} MP.{ui.RESET}")
        if item.get('cure'):
            cured = [s for s in item['cure'] if s in user.status]
            for s in cured:
                del user.status[s]
            self.log.add(f"{ui.BG}{user.name} uses {item['name']}.{ui.RESET}")

    def ally_turn(self, u):
        stance = getattr(u, 'stance', 'balanced')
        hurt_allies = [p for p in self.party if p.hp / p.max_hp < 0.4]
        heal_sid = next((sid for sid in u.skills if (get_skill(sid) or {}).get('kind') == 'support'), None)
        if stance in ('balanced', 'defensive', 'support') and hurt_allies and heal_sid:
            tgt = min(hurt_allies, key=lambda p: p.hp / p.max_hp)
            if u.mp >= get_skill(heal_sid).get('mp', 0):
                self.perform_skill(u, heal_sid, tgt)
                return
        if stance == 'defensive' and u.hp / u.max_hp < 0.5:
            u.guarding = True
            self.log.add(f'{ui.C}{u.name} guards cautiously.{ui.RESET}')
            return
        offense = [sid for sid in u.skills if (get_skill(sid) or {}).get('kind') == 'attack' and u.mp >= (get_skill(sid) or {}).get('mp', 0)]
        if offense and (stance == 'aggressive' or self.rng.random() < 0.7):
            sid = self.rng.choice(offense)
            s = get_skill(sid)
            if s.get('target') == 'enemy':
                tgt = self.rng.choice(self.foes)
                self.perform_skill(u, sid, tgt)
                return
            self.perform_skill(u, sid, None)
            return
        tgt = self.rng.choice(self.foes)
        self.basic_attack(u, tgt)

    def enemy_turn(self, e):
        offense = [sid for sid in e.skills if (get_skill(sid) or {}).get('kind') == 'attack' and e.mp >= (get_skill(sid) or {}).get('mp', 0)]
        if offense and self.rng.random() < 0.75:
            sid = self.rng.choice(offense)
            s = get_skill(sid)
            if s.get('target') == 'enemy':
                pool = [p for p in self.party if p.alive]
                if not pool:
                    return
                weights = [2.0 if p is self.hero else 1.0 for p in pool]
                tgt = self.rng.choices(pool, weights)[0]
                self.perform_skill(e, sid, tgt)
                return
            self.perform_skill(e, sid, None)
            return
        pool = [p for p in self.party if p.alive]
        if not pool:
            return
        weights = [2.0 if p is self.hero else 1.0 for p in pool]
        tgt = self.rng.choices(pool, weights)[0]
        self.basic_attack(e, tgt)

    def finish(self):
        out = {'result': self.result, 'rounds': self.round_no}
        deltas = []
        for sid, old in self.mastery_snapshot.items():
            new = self.hero.skills.get(sid, {}).get('mastery', old)
            if new > old:
                deltas.append((sid, new - old))
        out['mastery_deltas'] = sorted(deltas, key=lambda x: -x[1])[:4]
        if self.result == 'win':
            xp_total = sum((e.xp_reward for e in self.enemies))
            max_foe_lvl = max((e.level for e in self.enemies), default=1)
            gap = self.hero.level - max_foe_lvl
            if gap > 12:
                xp_total = int(xp_total * 0.08)
            elif gap > 6:
                xp_total = int(xp_total * 0.35)
            out['xp'] = xp_total
            drops = {}
            drop_bonus = 0
            if self.hero.has_skill('scent_track'):
                drop_bonus += get_skill('scent_track').get('drop_bonus', 10)
            if self.hero.has_skill('hunter_instinct'):
                drop_bonus += get_skill('hunter_instinct').get('drop_bonus', 20)
            for e in self.enemies:
                for mat, ch in e.drops:
                    ch2 = min(0.95, ch + drop_bonus / 100.0)
                    if self.rng.random() < ch2:
                        drops[mat] = drops.get(mat, 0) + 1
            out['drops'] = drops
        return out
