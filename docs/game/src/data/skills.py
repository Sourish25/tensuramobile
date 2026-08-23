SKILLS = {
    "absorb": {"name": "Absorb", "tier": "intrinsic", "kind": "utility", "desc": "Draw a defeated target into your body. Core of devouring."},
    "dissolve": {"name": "Dissolve", "tier": "intrinsic", "kind": "utility", "desc": "Break down absorbed matter into nutrients and analysis data."},
    "self_regen": {"name": "Self-Regeneration", "tier": "intrinsic", "kind": "passive", "desc": "Slowly regenerate HP every round.", "regen_pct": 0.04},
    "night_vision": {"name": "Night Vision", "tier": "intrinsic", "kind": "passive", "desc": "See in darkness. Improves accuracy in caves.", "acc_bonus": 5},
    "vigor": {"name": "Vigor", "tier": "intrinsic", "kind": "passive", "desc": "Robust vitality.", "stats": {"hp": 4}},
    "scale_body": {"name": "Scale Body", "tier": "intrinsic", "kind": "passive", "desc": "Hard scales blunt blows.", "stats": {"def": 4}},
    "swim": {"name": "Swim", "tier": "intrinsic", "kind": "passive", "desc": "Move freely in water."},
    "monstrous_str": {"name": "Monstrous Strength", "tier": "intrinsic", "kind": "passive", "desc": "Overwhelming raw power.", "stats": {"atk": 6}},
    "fear_aura": {"name": "Fear Aura", "tier": "intrinsic", "kind": "passive", "desc": "Your presence unnerves foes.", "debuff": {"atk": -2}},
    "scent_track": {"name": "Scent Track", "tier": "intrinsic", "kind": "passive", "desc": "Track prey by smell. Better drops.", "drop_bonus": 10},
    "sprint": {"name": "Sprint", "tier": "intrinsic", "kind": "passive", "desc": "Explosive footspeed.", "stats": {"agi": 5}},

    "tackle": {"name": "Tackle", "tier": "common", "kind": "attack", "element": "physical", "scale": "atk", "power": 10, "mp": 0, "target": "enemy", "desc": "A full-body ram."},
    "bite": {"name": "Bite", "tier": "common", "kind": "attack", "element": "physical", "scale": "atk", "power": 12, "mp": 0, "target": "enemy", "status": {"bleed": 0.2}, "desc": "Savage jaws."},
    "claw_swipe": {"name": "Claw Swipe", "tier": "common", "kind": "attack", "element": "physical", "scale": "atk", "power": 14, "mp": 1, "hits": 2, "target": "enemy", "desc": "Two raking claws."},
    "sharp_horn": {"name": "Sharp Horn", "tier": "common", "kind": "attack", "element": "physical", "scale": "atk", "power": 16, "mp": 2, "target": "enemy", "status": {"stun": 0.1}, "desc": "Goring thrust."},
    "body_slam": {"name": "Body Slam", "tier": "common", "kind": "attack", "element": "physical", "scale": "atk", "power": 18, "mp": 3, "target": "enemy", "desc": "Crushing weight."},
    "poison_sting": {"name": "Poison Sting", "tier": "common", "kind": "attack", "element": "physical", "scale": "atk", "power": 8, "mp": 2, "target": "enemy", "status": {"poison": 0.5}, "desc": "Venomous jab."},

    "magic_sense": {"name": "Magic Sense", "tier": "extra", "kind": "passive", "desc": "Perceive surroundings via magicules. +accuracy, reveals hidden foes.", "acc_bonus": 8},
    "sense_heat": {"name": "Sense Heat Source", "tier": "extra", "kind": "passive", "desc": "Detect warm bodies through obstacles.", "acc_bonus": 4, "crit_bonus": 3},
    "poison_breath": {"name": "Poisonous Breath", "tier": "extra", "kind": "attack", "element": "dark", "scale": "mag", "power": 14, "mp": 6, "target": "all_enemies", "status": {"poison": 0.35}, "desc": "Toxic mist over the field."},
    "paralysis_breath": {"name": "Paralyzing Breath", "tier": "extra", "kind": "attack", "element": "dark", "scale": "mag", "power": 10, "mp": 7, "target": "all_enemies", "status": {"paralysis": 0.3}, "desc": "Numbing fog."},
    "sticky_thread": {"name": "Sticky Thread", "tier": "extra", "kind": "attack", "element": "physical", "scale": "agi", "power": 8, "mp": 4, "target": "enemy", "status": {"bind": 0.45}, "desc": "Adhesive strands bind a target."},
    "steel_thread": {"name": "Steel Thread", "tier": "extra", "kind": "attack", "element": "physical", "scale": "agi", "power": 16, "mp": 6, "hits": 3, "target": "enemy", "desc": "Razor filaments cut repeatedly."},
    "drain_touch": {"name": "Drain", "tier": "extra", "kind": "attack", "element": "dark", "scale": "mag", "power": 12, "mp": 5, "target": "enemy", "drain": 0.5, "desc": "Steal vitality; half becomes your HP."},
    "ultrasonic_wave": {"name": "Ultrasonic Wave", "tier": "extra", "kind": "attack", "element": "wind", "scale": "mag", "power": 13, "mp": 5, "target": "all_enemies", "status": {"fear": 0.15}, "desc": "Disorienting resonance."},
    "water_blade": {"name": "Water Blade", "tier": "extra", "kind": "attack", "element": "water", "scale": "mag", "power": 16, "mp": 5, "target": "enemy", "desc": "A pressurized crescent of water."},
    "water_propulsion": {"name": "Water Pressure Propulsion", "tier": "extra", "kind": "utility", "desc": "Jet-propelled movement. Enables Current Movement."},
    "current_move": {"name": "Current Movement", "tier": "extra", "kind": "passive", "desc": "Flow like water in battle. +AGI.", "stats": {"agi": 4}},
    "fireball": {"name": "Fireball", "tier": "extra", "kind": "attack", "element": "fire", "scale": "mag", "power": 18, "mp": 6, "target": "enemy", "status": {"burn": 0.25}, "desc": "Hurl a searing orb."},
    "icicle_lance": {"name": "Icicle Lance", "tier": "extra", "kind": "attack", "element": "water", "scale": "mag", "power": 17, "mp": 5, "target": "enemy", "desc": "Impale with conjured ice. Cast instantly after absorption."},
    "stone_bullet": {"name": "Stone Bullet", "tier": "extra", "kind": "attack", "element": "earth", "scale": "mag", "power": 15, "mp": 4, "hits": 2, "target": "enemy", "desc": "Fired earthen rounds."},
    "wind_cutter": {"name": "Wind Cutter", "tier": "extra", "kind": "attack", "element": "wind", "scale": "mag", "power": 16, "mp": 5, "target": "enemy", "desc": "Blade of compressed air."},
    "lightning_bolt": {"name": "Lightning Bolt", "tier": "extra", "kind": "attack", "element": "lightning", "scale": "mag", "power": 22, "mp": 9, "target": "enemy", "status": {"paralysis": 0.2}, "desc": "A cracking arc of voltage."},
    "heal_minor": {"name": "Recovery Magic", "tier": "extra", "kind": "support", "element": "none", "scale": "mag", "power": 22, "mp": 8, "target": "ally", "desc": "Mend wounds with magicules."},
    "barrier_basic": {"name": "Barrier", "tier": "extra", "kind": "defense", "scale": "mag", "power": 20, "mp": 6, "target": "ally", "desc": "Magicule shield absorbing damage."},
    "flame_aura": {"name": "Control Flame", "tier": "extra", "kind": "passive", "desc": "Command fire at will. Fire power +15%.", "elem_boost": {"fire": 0.15}},
    "dark_flame": {"name": "Dark Flame", "tier": "extra", "kind": "attack", "element": "dark", "scale": "mag", "power": 20, "mp": 8, "target": "enemy", "status": {"burn": 0.35}, "desc": "Black fire that clings and consumes."},
    "gravity_flight": {"name": "Gravity Flight", "tier": "extra", "kind": "passive", "desc": "Fly freely. +AGI, evade first strike.", "stats": {"agi": 6}},

    "hellflare": {"name": "Hellflare", "tier": "unique", "kind": "attack", "element": "fire", "scale": "mag", "power": 55, "mp": 25, "target": "all_enemies", "status": {"burn": 0.6}, "desc": "Dome of thousands-degree flame razing the field."},
    "megiddo": {"name": "Megiddo", "tier": "unique", "kind": "attack", "element": "holy", "scale": "mag", "power": 70, "mp": 30, "hits": 5, "target": "single_strongest", "pierce_barrier": True, "desc": "Water elementals refract sunlight into soundless light-speed bolts. Ignores barriers."},
    "thousand_shadow_death": {"name": "Thousand Shadow Death", "tier": "unique", "kind": "attack", "element": "dark", "scale": "agi", "power": 60, "mp": 28, "hits": 4, "target": "all_enemies", "desc": "Shadow clones erupt and strike from every angle."},

    "great_sage": {"name": "Great Sage", "tier": "unique", "kind": "passive", "latent_of": "slime", "desc": "Hasten Thought x1000, Analyze and Assess, Parallel Operation. Mastery gain doubled; battle reports enabled.", "mastery_mult": 2.0, "analysis_instant": True},
    "predator": {"name": "Predator", "tier": "unique", "kind": "passive", "latent_of": "slime", "desc": "Predation, Analysis, Stomach, Mimicry, Isolate. Unlocks true devouring.", "devour_master": True},
    "born_leader": {"name": "Born Leader", "tier": "unique", "kind": "passive", "latent_of": "goblin", "desc": "Compute Prediction: read enemy moves. Party ATK +10%, your accuracy +15%.", "party_atk_pct": 0.10, "acc_bonus": 15},
    "tyrant_edge": {"name": "Tyrant Edge", "tier": "unique", "kind": "passive", "latent_of": "lizardman", "desc": "The blade-dominion of a would-be king. Crit chance +20%, physical power +12%.", "crit_bonus": 20, "phys_pct": 0.12},
    "berserker": {"name": "Berserker", "tier": "unique", "kind": "passive", "latent_of": "ogre", "desc": "Strength grows as death approaches: up to +50% ATK below 30% HP.", "rage_scaling": True},
    "hunter_instinct": {"name": "Hunter Instinct", "tier": "unique", "kind": "passive", "latent_of": "direwolf", "desc": "Always strike first in round one; +15% dodge; prey drop rates +20%.", "first_strike": True, "dodge_bonus": 15, "drop_bonus": 20},

    "raphael": {"name": "Raphael, Lord of Wisdom", "tier": "ultimate", "kind": "passive", "desc": "Ultimate wisdom. All mastery gain tripled; battle analysis; counter-computation of enemy kits.", "mastery_mult": 3.0, "ultimate_aura": True},
    "belzebuth": {"name": "Belzebuth, Lord of Gluttony", "tier": "ultimate", "kind": "passive", "desc": "Soul Consume and Food Chain. Devour weakened foes mid-battle.", "devour_master": True, "midbattle_consume": True, "ultimate_aura": True},

    "azathoth": {"name": "Azathoth, God of the Void", "tier": "ultimate", "kind": "passive", "desc": "The void god's authority. Void Collapse energy, Complex Space, all gluttony and wisdom subsumed. Party-wide +15% to all stats.", "ultimate_aura": True, "party_all_pct": 0.15, "void_authority": True},
    "amaterasu_u": {"name": "Amaterasu, Lord of Shimmering Flame", "tier": "ultimate", "kind": "passive", "desc": "Hive-command flame authority. Party ATK +18%, your fire power +30%.", "ultimate_aura": True, "party_atk_pct": 0.18, "elem_boost": {"fire": 0.30}},
    "nyarlathotep": {"name": "Nyarlathotep, Lord of Chaos", "tier": "ultimate", "kind": "passive", "desc": "Storm-dragon chaos. Parallel Existence (survive lethal once per battle), Control Probability (+25% crit, +15% dodge).", "ultimate_aura": True, "crit_bonus": 25, "dodge_bonus": 15, "parallel_existence": True},
    "susano_oh": {"name": "Susano-oh, King of Atrocity", "tier": "ultimate", "kind": "passive", "desc": "Nihilistic Cancel: incoming skill damage -25%. Rage scaling amplified x2.", "ultimate_aura": True, "dmg_reduction": 0.25, "rage_x2": True},
    "hastur": {"name": "Hastur, Lord of the Hunt", "tier": "ultimate", "kind": "passive", "desc": "Weather dominion. Always act first, +30% AGI, prey drops doubled.", "ultimate_aura": True, "first_strike": True, "stats": {"agi": 12}, "drop_bonus": 100},

    "soul_consume": {"name": "Soul Consume", "tier": "ultimate", "kind": "attack", "element": "dark", "scale": "mag", "power": 80, "mp": 35, "target": "enemy", "execute_below": 0.20, "drain": 0.6, "desc": "Devour a weakened foe body and soul. Instantly consumes targets below 20% HP."},
    "void_collapse": {"name": "Void Collapse", "tier": "ultimate", "kind": "attack", "element": "void", "scale": "mag", "power": 120, "mp": 60, "target": "all_enemies", "pierce_barrier": True, "desc": "The primordial energy that built worlds, released as annihilation. Ignores all barriers."},
    "melt_slash": {"name": "Melt Slash", "tier": "ultimate", "kind": "attack", "element": "holy", "scale": "atk", "power": 95, "mp": 40, "target": "enemy", "pierce_barrier": True, "status": {"seal": 0.4}, "desc": "Disintegration poured along a blade at supersonic speed. Pierces everything, seals skills."},
    "white_flare": {"name": "White Flare", "tier": "ultimate", "kind": "attack", "element": "fire", "scale": "mag", "power": 110, "mp": 50, "target": "enemy", "pierce_barrier": True, "desc": "Single-target white annihilation. Heat above nuclear magic with zero spill."},
    "time_stop": {"name": "Time Stop", "tier": "ultimate", "kind": "attack", "element": "void", "scale": "none", "power": 0, "mp": 45, "target": "all_enemies", "status": {"stun": 1.0}, "desc": "Freeze the world's flow. All enemies lose their next action."},
    "dominate_space": {"name": "Dominate Space", "tier": "ultimate", "kind": "attack", "element": "void", "scale": "none", "power": 0, "mp": 40, "target": "all_enemies", "status": {"bind": 2}, "fear": None, "desc": "Seize local space-time: enemies bound and unable to flee or maneuver."},
    "creations_blade": {"name": "All of Creation: Blade", "tier": "ultimate", "kind": "attack", "element": "physical", "scale": "atk", "power": 105, "mp": 45, "hits": 3, "target": "single_strongest", "desc": "Raphael computes the perfect thousand-cut sequence against the strongest foe."},

    "jibril_reflect": {"name": "Jibril, Lord of Rigor", "tier": "ultimate", "kind": "passive", "desc": "Divine Judgment: reflects 40% of damage taken back upon attackers.", "ultimate_aura": True},
    "sandalphon_u": {"name": "Sandalphon, Lord of Judgment", "tier": "ultimate", "kind": "attack", "element": "holy", "scale": "mag", "power": 90, "mp": 40, "target": "single_strongest", "status": {"judgment": 2}, "desc": "Heaven's verdict marks a foe; their blows turn upon themselves."},
    "regalia_dominion": {"name": "Regalia Dominion", "tier": "ultimate", "kind": "attack", "element": "dark", "scale": "none", "power": 0, "mp": 55, "target": "single_strongest", "status": {"stun": 2}, "desc": "Kneel. A lesser will is overwritten for two turns."},

    "magic_interference_f": {"name": "Magic Interference", "tier": "extra", "kind": "passive", "desc": "Emit a field that dampens enemy spellpower by half.", "spell_suppress_own": True},

    "ravenous": {"name": "Ravenous", "tier": "unique", "kind": "passive", "desc": "Starvation made strength. Basic attacks heal 20% of damage dealt.", "lifesteal_basic": 0.20},
    "rot_aura": {"name": "Rot Aura", "tier": "extra", "kind": "attack", "element": "dark", "scale": "mag", "power": 18, "mp": 10, "target": "all_enemies", "status": {"poison": 0.5, "burn": 0.3}, "desc": "Corrupting miasma rots flesh and steel alike."},
    "death_march": {"name": "Death March Dance", "tier": "extra", "kind": "attack", "element": "dark", "scale": "atk", "power": 26, "mp": 14, "hits": 5, "target": "all_enemies", "desc": "A whirling dance of cleaver-arcs that scatters death across the field."},
    "tempest_scale": {"name": "Tempest Scale Volley", "tier": "extra", "kind": "attack", "element": "wind", "scale": "agi", "power": 22, "mp": 12, "hits": 6, "target": "enemy", "desc": "Loosed scales ride the storm like bullets."},
    "flame_breath_u": {"name": "Dragon Flame Breath", "tier": "unique", "kind": "attack", "element": "fire", "scale": "mag", "power": 48, "mp": 30, "target": "all_enemies", "status": {"burn": 0.5}, "desc": "A dragon's exhale reduces terrain to glass."},
    "cardinal_acceleration": {"name": "Cardinal Acceleration", "tier": "ultimate", "kind": "attack", "element": "fire", "scale": "agi", "power": 150, "mp": 70, "target": "single_strongest", "pierce_barrier": True, "desc": "Thousands of times the speed of sound folded into one guided strike."},
    "parallel_existence": {"name": "Parallel Existence", "tier": "ultimate", "kind": "passive", "desc": "Death is negotiable: survive lethal damage once per battle.", "ultimate_aura": True},
    "raguel_amp": {"name": "Raguel's Amplification", "tier": "unique", "kind": "support", "element": "none", "scale": "none", "power": 0, "mp": 25, "target": "ally", "status": {"amp": 3}, "desc": "The world's energy bends to magnify an ally's output (+40% ATK/MAG)."},
}

RECIPES = [
    ("water_blade", "water_propulsion", "control_water"),
    ("sticky_thread", "steel_thread", "sticky_steel_thread"),
]

COMBO_SKILLS = {
    "control_water": {
        "name": "Control Water", "tier": "extra", "kind": "attack", "element": "water", "scale": "mag",
        "power": 26, "mp": 8, "target": "all_enemies", "parents": ["water_blade", "water_propulsion"],
        "desc": "Total dominion of liquids. Waves strike all foes.",
        "grants_passive": {"stats": {"agi": 3}},
    },
    "sticky_steel_thread": {
        "name": "Sticky Steel Thread", "tier": "extra", "kind": "attack", "element": "physical", "scale": "agi",
        "power": 24, "mp": 9, "hits": 4, "target": "enemy", "status": {"bind": 0.5},
        "parents": ["sticky_thread", "steel_thread"],
        "desc": "Filaments both adhesive and razor-sharp.",
    },
}

MASTERY_RANKS = [(0, "Novice"), (25, "Adept"), (50, "Expert"), (75, "Master"), (100, "Perfected")]


def mastery_rank(m):
    r = MASTERY_RANKS[0][1]
    for th, name in MASTERY_RANKS:
        if m >= th:
            r = name
    return r


def get_skill(sid):
    return SKILLS.get(sid) or COMBO_SKILLS.get(sid)


def skill_name(sid):
    s = get_skill(sid)
    return s["name"] if s else sid


ELEMENT_MULT = {
    "fire": {"water": 1.5, "fire": 0.5, "earth": 0.75, "wind": 1.0, "lightning": 1.0, "ice": 0.5},
    "water": {"fire": 1.5, "water": 0.5, "earth": 1.25, "lightning": 1.5},
    "wind": {"earth": 1.25, "wind": 0.5},
    "earth": {"lightning": 0.5, "wind": 1.25},
    "lightning": {"water": 1.5, "earth": 1.5, "lightning": 0.5},
    "holy": {"dark": 1.75, "holy": 0.25},
    "dark": {"holy": 0.25, "dark": 0.75},
}


def element_mult(atk_el, def_el):
    return ELEMENT_MULT.get(atk_el, {}).get(def_el, 1.0)
