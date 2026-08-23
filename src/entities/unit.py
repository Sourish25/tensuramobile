from src.data import races as races_data
from src.data.skills import get_skill, skill_name
from src.data.items import ITEMS


def rank_from_ep(ep):
    if ep >= 1_000_000:
        return "Million"
    if ep >= 800_000:
        return "Special S"
    if ep >= 400_000:
        return "S"
    if ep >= 100_000:
        return "Special A"
    if ep >= 40_000:
        return "A+"
    if ep >= 20_000:
        return "A"
    if ep >= 10_000:
        return "B+"
    if ep >= 6_000:
        return "B"
    if ep >= 3_000:
        return "C"
    if ep >= 1_200:
        return "D"
    if ep >= 400:
        return "E"
    return "F"


class Unit:
    def __init__(self, name, glyph="?", color="\033[37m"):
        self.name = name
        self.glyph = glyph
        self.color = color
        self.level = 1
        self.stats = {"hp": 50, "mp": 30, "atk": 8, "def": 5, "mag": 6, "spr": 5, "agi": 8}
        self.hp = self.stats["hp"]
        self.mp = self.stats["mp"]
        self.skills = {}
        self.status = {}
        self.guarding = False
        self.barrier_hp = 0
        self.is_boss = False
        self.element = None
        self.desc = ""
        self.gimmicks = {}
        self.barrier_field_hp = 0
        self.phase_data = None
        self.phase_idx = 0
    @property
    def max_hp(self):
        return self.stats["hp"]

    @property
    def max_mp(self):
        return self.stats["mp"]

    @property
    def alive(self):
        return self.hp > 0

    def has_skill(self, sid):
        return sid in self.skills

    def learn_skill(self, sid, mastery=0):
        if sid and sid not in self.skills:
            self.skills[sid] = {"mastery": mastery}

    def passive_stat_bonus(self):
        bonus = {}
        for sid in self.skills:
            s = get_skill(sid)
            if not s:
                continue
            for k, v in (s.get("stats") or {}).items():
                bonus[k] = bonus.get(k, 0) + v
        return bonus

    def eff_stat(self, key):
        v = self.stats[key] + self.passive_stat_bonus().get(key, 0)
        st = self.status
        if key == "atk" and ("fear" in st or "fear_aura_debuff" in st):
            v = int(v * 0.85)
        if key == "agi" and "bind" in st:
            v = int(v * 0.4)
        if key == "agi" and "paralysis" in st:
            v = int(v * 0.5)
        return v

    def add_status(self, sid, turns=3):
        if sid == "stun":
            turns = 1
        cur = self.status.get(sid)
        self.status[sid] = max(cur or 0, turns)

    def tick_statuses(self):
        expired = []
        regen = 0
        for sid in list(self.status.keys()):
            if sid == "burn":
                dmg = max(2, int(self.max_hp * 0.03))
                self.hp -= dmg
                regen += 0
                self._last_dot = dmg
            elif sid == "poison":
                dmg = max(2, int(self.max_hp * 0.04))
                self.hp -= dmg
                self._last_dot = dmg
            elif sid == "bleed":
                dmg = max(1, int(self.max_hp * 0.02))
                self.hp -= dmg
                self._last_dot = dmg
            self.status[sid] -= 1
            if self.status[sid] <= 0:
                expired.append(sid)
        for sid in expired:
            del self.status[sid]
        if self.has_skill("self_regen") and self.alive:
            regen += max(1, int(self.max_hp * 0.04))
        if regen and self.alive:
            self.hp = min(self.max_hp, self.hp + regen)
        return expired

    def is_acting_blocked(self):
        if not self.alive:
            return True
        if "paralysis" in self.status and self._rng() < 0.5:
            return True
        if "stun" in self.status:
            return True
        return False

    def _rng(self):
        import random
        return random.random()


class Player(Unit):
    def __init__(self, name, race_id):
        super().__init__(name)
        r = races_data.RACES[race_id]
        self.race_id = race_id
        self.glyph = r["glyph"]
        self.color = races_data.COLORS[r["color"]]
        self.level = 1
        self.xp = 0
        self.gold = 50
        self.souls = 0
        self.stats = dict(r["base"])
        self.hp = self.stats["hp"]
        self.mp = self.stats["mp"]
        self.mp_scar = 0.0
        for sid in r["intrinsics"]:
            self.learn_skill(sid)
        self.latent_unlocked = False
        self.stomach = {}
        self.materials = {}
        self.consumables = {"low_potion": 2}
        self.gear = {"weapon": None, "armor": None}
        self.mimic_forms = []
        self.active_form = None
        self.form_cooldown = 0
        self.devour_count = 0
        self.kills = 0
        self.phase = 0
        self.demon_lord = False
        self.godhood = False
        self.party_ids = []

    @property
    def max_hp(self):
        return self.stats["hp"]

    @property
    def max_mp(self):
        return max(10, int(self.stats["mp"] - self.mp_scar))

    @property
    def alive(self):
        return self.hp > 0

    def has_skill(self, sid):
        return sid in self.skills

    def learn_skill(self, sid, mastery=0):
        if sid and sid not in self.skills:
            self.skills[sid] = {"mastery": mastery}

    @property
    def stage_name(self):
        return races_data.evolution_stage(self.race_id, self.level)["name"]

    def xp_to_next(self):
        return int(60 * (self.level ** 1.55))

    def gain_xp(self, amount):
        leveled = []
        self.xp += amount
        while self.xp >= self.xp_to_next():
            self.xp -= self.xp_to_next()
            self.level_up()
            leveled.append(self.level)
        return leveled

    def level_up(self):
        if self.level >= 100:
            self.hp = self.max_hp
            self.mp = self.max_mp
            return "capped"
        g = races_data.RACES[self.race_id]["growth"]
        for k, v in g.items():
            self.stats[k] += v
        self.level += 1
        self.hp = self.max_hp
        self.mp = self.max_mp
        evo = races_data.evolution_stage(self.race_id, self.level)
        for sid in evo.get("grants", []):
            self.learn_skill(sid)
        r = races_data.RACES[self.race_id]
        if not self.latent_unlocked and self.level >= r["latent_level"]:
            self.latent_unlocked = True
            for sid in r["latent_unique"]:
                self.learn_skill(sid)
            return "latent"
        return "normal"

    def check_evolution(self):
        prev = getattr(self, "_evo_stage", None)
        cur = races_data.evolution_stage(self.race_id, self.level)["name"]
        if prev and prev != cur:
            mult = races_data.evolution_stage(self.race_id, self.level)["mult"]
            for k in ("hp", "mp", "atk", "def", "mag", "spr"):
                self.stats[k] = int(self.stats[k] * mult.get(k, 1.0))
            self.hp = self.max_hp
            self.mp = self.max_mp
        self._evo_stage = cur
        return prev != cur if prev else False

    def weapon_atk(self):
        w = self.gear.get("weapon")
        if w:
            return ITEMS[w].get("atk", 0)
        return 0

    def armor_def(self):
        a = self.gear.get("armor")
        if a:
            return ITEMS[a].get("def", 0)
        return 0

    def compute_ep(self):
        stat_sum = sum(self.stats.values()) + self.weapon_atk() + self.armor_def()
        skill_power = 0
        for sid, data in self.skills.items():
            s = get_skill(sid)
            if not s:
                continue
            tier_w = {"common": 20, "extra": 90, "unique": 600, "ultimate": 4000}.get(s["tier"], 5)
            skill_power += tier_w * (1 + data["mastery"] / 100.0)
        ep = int(stat_sum ** 2.05 / 22 + skill_power)
        return max(ep, 10)

    def name_cost_pct(self, target_ep):
        if target_ep >= 4000:
            return 0.45
        if target_ep >= 1500:
            return 0.30
        if target_ep >= 500:
            return 0.22
        return 0.15

    def can_afford_name(self, target_ep):
        cost = int(self.stats["mp"] * self.name_cost_pct(target_ep))
        return (self.stats["mp"] - self.mp_scar) - cost >= self.stats["mp"] * 0.10, cost

    def pay_name_cost(self, cost):
        self.mp_scar += cost
        self.mp = min(self.mp, self.max_mp)

    def recover_scar_on_rest(self):
        heal = self.stats["mp"] * 0.18
        before = self.mp_scar
        self.mp_scar = max(0.0, self.mp_scar - heal)
        return round(before - self.mp_scar)

    def to_dict(self):
        return {
            "kind": "player",
            "name": self.name,
            "race_id": self.race_id,
            "level": self.level,
            "xp": self.xp,
            "gold": self.gold,
            "souls": self.souls,
            "stats": dict(self.stats),
            "skills": {sid: d["mastery"] for sid, d in self.skills.items()},
            "latent_unlocked": self.latent_unlocked,
            "stomach": dict(self.stomach),
            "materials": dict(self.materials),
            "consumables": dict(self.consumables),
            "gear": dict(self.gear),
            "mimic_forms": list(self.mimic_forms),
            "devour_count": self.devour_count,
            "kills": self.kills,
            "phase": self.phase,
            "mp_scar": self.mp_scar,
            "demon_lord": self.demon_lord,
            "godhood": self.godhood,
            "_evo_stage": getattr(self, "_evo_stage", None),
        }

    @classmethod
    def from_dict(cls, d):
        p = cls(d["name"], d["race_id"])
        p.level = d["level"]
        p.xp = d["xp"]
        p.gold = d["gold"]
        p.souls = d.get("souls", 0)
        p.stats = dict(d["stats"])
        p.skills = {}
        from src.data.skills import get_skill as gs
        for sid, m in d["skills"].items():
            if gs(sid):
                p.learn_skill(sid)
                p.skills[sid]["mastery"] = m
        p.latent_unlocked = d.get("latent_unlocked", False)
        p.stomach = dict(d.get("stomach", {}))
        p.materials = dict(d.get("materials", {}))
        p.consumables = dict(d.get("consumables", {}))
        p.gear = dict(d.get("gear", {}))
        p.mimic_forms = list(d.get("mimic_forms", []))
        p.devour_count = d.get("devour_count", 0)
        p.kills = d.get("kills", 0)
        p.phase = d.get("phase", 0)
        p.mp_scar = d.get("mp_scar", 0.0)
        p.demon_lord = d.get("demon_lord", False)
        p.godhood = d.get("godhood", False)
        p._evo_stage = d.get("_evo_stage")
        p.hp = min(p.max_hp, p.stats["hp"])
        p.mp = min(p.max_mp, p.stats["mp"])
        return p


class Subordinate(Unit):
    def __init__(self, name, species_key, level=1):
        from src.data.monsters import MONSTERS
        t = MONSTERS[species_key]
        super().__init__(name, t["glyph"], "\033[92m")
        self.species = species_key
        self.template_ep = t["ep"]
        self.level = level
        scale = 1 + (level - 1) * 0.18
        self.stats = {k: int(v * scale) for k, v in t["stats"].items()}
        self.hp = self.stats["hp"]
        self.mp = self.stats["mp"]
        for sid in t["skills"]:
            self.learn_skill(sid, mastery=35)
        self.loyalty = 70
        self.assignment = "party"
        self.stance = "balanced"
        self.xp = 0
        self.evolve_name = None
        self.evolve_glyph = None

    @property
    def display_name(self):
        return f"{self.name} ({self.evolve_name or self.species.replace('_', ' ').title()})"

    def xp_to_next(self):
        return int(45 * (self.level ** 1.55))

    def gain_xp(self, amount):
        leveled = []
        self.xp += amount
        while self.xp >= self.xp_to_next():
            self.xp -= self.xp_to_next()
            self.level_up()
            leveled.append(self.level)
        return leveled

    def level_up(self):
        self.level += 1
        for k in self.stats:
            self.stats[k] = int(self.stats[k] * 1.13) + 1
        self.hp = self.max_hp
        self.mp = self.max_mp
        return self.level

    def apply_named_form(self):
        from src.data.monsters import MONSTERS
        t = MONSTERS[self.species]
        evo = t.get("evolve")
        if not evo:
            return None
        for k in self.stats:
            self.stats[k] = int(self.stats[k] * evo.get("mult", {}).get(k, 1.15))
        self.evolve_name = evo["name"]
        self.evolve_glyph = evo.get("glyph", self.glyph)
        self.glyph = self.evolve_glyph
        for sid in evo.get("grant_skills", []):
            self.learn_skill(sid)
        self.element = t.get("element")
        return evo["name"]

    def named_evolve_boost(self):
        for k in self.stats:
            self.stats[k] = int(self.stats[k] * 1.2) + 3
        self.hp = self.max_hp
        self.mp = self.max_mp

    def to_dict(self):
        return {
            "kind": "sub",
            "name": self.name,
            "species": self.species,
            "level": self.level,
            "xp": getattr(self, "xp", 0),
            "stats": dict(self.stats),
            "skills": {sid: d["mastery"] for sid, d in self.skills.items()},
            "loyalty": self.loyalty,
            "assignment": self.assignment,
            "stance": self.stance,
            "evolve_name": self.evolve_name,
            "evolve_glyph": self.evolve_glyph,
        }

    @classmethod
    def from_dict(cls, d):
        s = cls(d["name"], d["species"], level=d.get("level", 1))
        s.xp = d.get("xp", 0)
        s.stats = dict(d["stats"])
        s.skills = {}
        from src.data.skills import get_skill as gs
        for sid, m in d.get("skills", {}).items():
            if gs(sid):
                s.learn_skill(sid)
                s.skills[sid]["mastery"] = m
        s.loyalty = d.get("loyalty", 70)
        s.assignment = d.get("assignment", "bench")
        s.stance = d.get("stance", "balanced")
        s.evolve_name = d.get("evolve_name")
        s.evolve_glyph = d.get("evolve_glyph")
        if s.evolve_glyph:
            s.glyph = s.evolve_glyph
        s.hp = min(s.max_hp, s.stats["hp"])
        s.mp = min(s.max_mp, s.stats["mp"])
        return s


def enemy_from_template(mid, floor_scale=1.0):
    from src.data.monsters import MONSTERS
    from src.core.ui import ENEMY_C
    t = MONSTERS[mid]
    u = Unit(t["name"], t["glyph"], ENEMY_C)
    u.monster_id = mid
    u.level = t["level"]
    u.ep_value = t["ep"]
    u.is_boss = t.get("boss", False)
    u.element = t.get("element")
    u.desc = t.get("desc", "")
    u.xp_reward = t["xp"]
    u.drops = t["drops"]
    u.stealable = t["stealable"]
    u.signature_skill = t.get("signature_skill")
    u.gimmicks = dict(t.get("gimmicks", {}))
    u.phase_data = t.get("phases")
    u.barrier_field_hp = int(u.gimmicks.get("barrier_field", 0) * floor_scale)
    scale = floor_scale
    u.stats = {k: max(1, int(v * scale)) for k, v in t["stats"].items()}
    if u.gimmicks.get("spell_suppress"):
        pass
    u.hp = u.stats["hp"]
    u.mp = u.stats["mp"]
    for sid in t["skills"]:
        u.learn_skill(sid)
    return u
