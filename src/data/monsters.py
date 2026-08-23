MONSTERS = {
    "black_serpent": {
        "name": "Black Serpent", "glyph": "S", "ep": 90, "level": 1,
        "stats": {"hp": 34, "mp": 12, "atk": 10, "def": 4, "mag": 6, "spr": 4, "agi": 11},
        "element": None, "skills": ["bite", "poison_sting"],
        "xp": 22, "drops": [("snake_skin", 0.6), ("magic_crystal_shard", 0.3)],
        "stealable": ["sense_heat"],
    },
    "cave_centipede": {
        "name": "Evil Centipede", "glyph": "m", "ep": 160, "level": 2,
        "stats": {"hp": 53, "mp": 15, "atk": 14, "def": 7, "mag": 5, "spr": 5, "agi": 10},
        "element": None, "skills": ["bite", "paralysis_breath"],
        "xp": 40, "drops": [("chitin_plate", 0.55), ("magic_crystal_shard", 0.35)],
        "stealable": ["paralysis_breath"],
    },
    "black_spider": {
        "name": "Black Spider", "glyph": "x", "ep": 210, "level": 3,
        "stats": {"hp": 64, "mp": 24, "atk": 17, "def": 9, "mag": 9, "spr": 7, "agi": 17},
        "element": None, "skills": ["bite", "sticky_thread", "steel_thread"],
        "xp": 55, "drops": [("spider_silk", 0.65), ("spider_fang", 0.3)],
        "stealable": ["sticky_thread", "steel_thread"],
    },
    "giant_bat": {
        "name": "Giant Bat", "glyph": "v", "ep": 140, "level": 2,
        "stats": {"hp": 42, "mp": 20, "atk": 12, "def": 4, "mag": 11, "spr": 6, "agi": 17},
        "element": None, "skills": ["drain_touch", "ultrasonic_wave"],
        "xp": 35, "drops": [("bat_wing", 0.6)],
        "stealable": ["drain_touch", "ultrasonic_wave"],
    },
    "horned_rabbit": {
        "name": "Horned Rabbit", "glyph": "q", "ep": 60, "level": 1,
        "stats": {"hp": 26, "mp": 8, "atk": 9, "def": 3, "mag": 2, "spr": 3, "agi": 15},
        "element": None, "skills": ["tackle", "sharp_horn"],
        "xp": 14, "drops": [("fluffy_fur", 0.7), ("rabbit_horn", 0.25)],
        "stealable": ["sprint"],
        "evolve": {"name": "Horned King Rabbit", "glyph": "Q", "mult": {"hp": 1.3, "atk": 1.35, "def": 1.25, "agi": 1.2}},
    },
    "giant_ant": {
        "name": "Giant Ant", "glyph": "a", "ep": 130, "level": 2,
        "stats": {"hp": 51, "mp": 8, "atk": 14, "def": 10, "mag": 3, "spr": 6, "agi": 11},
        "element": None, "skills": ["bite", "claw_swipe"],
        "xp": 32, "drops": [("chitin_plate", 0.5), ("ant_mandible", 0.3)],
        "stealable": [],
    },
    "dire_wolf": {
        "name": "Direwolf", "glyph": "w", "ep": 180, "level": 3,
        "stats": {"hp": 62, "mp": 14, "atk": 18, "def": 7, "mag": 4, "spr": 6, "agi": 18},
        "element": None, "skills": ["bite", "claw_swipe"],
        "xp": 46, "drops": [("wolf_fang", 0.55), ("wolf_pelt", 0.45)],
        "stealable": ["sprint"],
        "evolve": {"name": "Tempest Wolf", "glyph": "W", "mult": {"hp": 1.35, "atk": 1.4, "def": 1.25, "agi": 1.3}, "grant_skills": ["wind_cutter"]},
    },
    "dire_alpha": {
        "name": "Direwolf Pack Leader", "glyph": "D", "ep": 3400, "level": 10, "boss": True,
        "stats": {"hp": 353, "mp": 83, "atk": 49, "def": 27, "mag": 20, "spr": 22, "agi": 39},
        "element": None, "skills": ["bite", "claw_swipe", "ultrasonic_wave"],
        "xp": 850, "drops": [("alpha_fang", 1.0), ("magic_crystal_small", 0.8)],
        "stealable": ["sprint", "ultrasonic_wave"], "signature_skill": "ultrasonic_wave",
        "sparable": True,
        "desc": "Alpha of the black wolf pack that hunts the forest edge.",
        "evolve": {"name": "Tempest Star Wolf", "glyph": "V", "mult": {"hp": 1.4, "atk": 1.45, "def": 1.3, "agi": 1.35, "mag": 1.4}},
    },
    "goblin": {
        "name": "Goblin", "glyph": "g", "ep": 70, "level": 1,
        "stats": {"hp": 30, "mp": 10, "atk": 9, "def": 5, "mag": 4, "spr": 4, "agi": 10},
        "element": None, "skills": ["tackle"],
        "xp": 16, "drops": [("fluffy_fur", 0.2)],
        "stealable": ["vigor"],
        "evolve": {"name": "Hobgoblin", "glyph": "G", "mult": {"hp": 1.5, "mp": 1.4, "atk": 1.5, "def": 1.4, "agi": 1.25}},
    },
    "mercenary": {
        "name": "Free Guild Mercenary", "glyph": "P", "ep": 900, "level": 8,
        "stats": {"hp": 202, "mp": 55, "atk": 40, "def": 25, "mag": 14, "spr": 18, "agi": 23},
        "element": None, "skills": ["claw_swipe", "body_slam", "heal_minor"],
        "xp": 220, "drops": [("magic_crystal_shard", 0.6), ("iron_dagger", 0.08)],
        "stealable": [],
        "desc": "A sellsword with coin-bought gear.",
    },
    "holy_knight": {
        "name": "Church Paladin", "glyph": "+", "ep": 1800, "level": 11,
        "stats": {"hp": 352, "mp": 132, "atk": 59, "def": 39, "mag": 39, "spr": 48, "agi": 26},
        "element": "holy", "skills": ["lightning_bolt", "barrier_basic", "sharp_horn"],
        "xp": 450, "drops": [("magic_crystal_small", 0.7)],
        "stealable": ["barrier_basic"],
        "desc": "Holy armor gleaming with self-righteousness.",
    },
    "armorsaurus": {
        "name": "Armorsaurus", "glyph": "A", "ep": 2200, "level": 8, "boss": True,
        "stats": {"hp": 349, "mp": 55, "atk": 44, "def": 33, "mag": 14, "spr": 22, "agi": 12},
        "element": "earth", "skills": ["body_slam", "stone_bullet", "bite"],
        "xp": 550, "drops": [("armor_scale", 1.0), ("magic_crystal_small", 0.7)],
        "stealable": ["scale_body", "body_slam"], "signature_skill": "scale_body",
        "desc": "A lizard clad in natural plate armor.",
    },
    "tempest_serpent": {
        "name": "Tempest Serpent", "glyph": "W", "ep": 8000, "level": 12, "boss": True,
        "stats": {"hp": 742, "mp": 185, "atk": 74, "def": 51, "mag": 60, "spr": 46, "agi": 41},
        "element": "wind", "skills": ["wind_cutter", "ultrasonic_wave", "bite", "water_blade"],
        "xp": 2000, "drops": [("serpent_core", 1.0), ("magic_crystal_small", 0.9), ("storm_scale", 0.8)],
        "stealable": ["wind_cutter", "current_move", "gravity_flight"], "signature_skill": "gravity_flight",
        "desc": "Guardian of the cave's depths. A-ranked menace.",
    },
    "orc_soldier": {
        "name": "Orc Soldier", "glyph": "n", "ep": 400, "level": 6,
        "stats": {"hp": 124, "mp": 22, "atk": 30, "def": 19, "mag": 6, "spr": 11, "agi": 12},
        "element": None, "skills": ["claw_swipe", "body_slam"],
        "xp": 100, "drops": [("orc_tusk", 0.5), ("crude_axe", 0.2), ("magic_crystal_shard", 0.4)],
        "stealable": ["monstrous_str"],
        "evolve": {"name": "High Orc", "glyph": "H", "mult": {"hp": 1.45, "atk": 1.35, "def": 1.4, "spr": 1.3}},
    },
    "orc_general": {
        "name": "Orc General", "glyph": "N", "ep": 1500, "level": 9,
        "stats": {"hp": 294, "mp": 47, "atk": 50, "def": 33, "mag": 11, "spr": 19, "agi": 17},
        "element": None, "skills": ["body_slam", "sharp_horn", "fear_roar"],
        "xp": 380, "drops": [("orc_tusk", 0.8), ("general_halberd", 0.15), ("magic_crystal_small", 0.5)],
        "stealable": ["fear_aura", "monstrous_str"],
        "evolve": {"name": "Orc King", "glyph": "K", "mult": {"hp": 1.5, "atk": 1.4, "def": 1.4, "mag": 1.3}},
    },
}

SKILL_GRANTS = {
    "fear_roar": {"name": "Fear Roar", "tier": "extra", "kind": "attack", "element": "dark", "scale": "mag", "power": 8, "mp": 6, "target": "all_enemies", "status": {"fear": 0.5}, "desc": "A roar that crushes morale."},
}

for sid, s in SKILL_GRANTS.items():
    from src.data.skills import SKILLS
    SKILLS.setdefault(sid, s)

FACTION_SQUADS = {
    "church": ["holy_knight", "mercenary"],
    "dwargon": ["mercenary", "mercenary"],
    "blumund": ["mercenary"],
    "guild": ["mercenary", "mercenary", "mercenary"],
}

MONSTERS.update({
    "orc_rider": {
        "name": "Orc Rider", "glyph": "r", "ep": 700, "level": 7,
        "stats": {"hp": 163, "mp": 27, "atk": 36, "def": 22, "mag": 8, "spr": 13, "agi": 24},
        "element": None, "skills": ["sharp_horn", "claw_swipe"],
        "xp": 170, "drops": [("orc_tusk", 0.6), ("magic_crystal_shard", 0.4)],
        "stealable": ["monstrous_str"],
    },
    "orc_lord_geld": {
        "name": "Orc Disaster Geld", "glyph": "G", "ep": 12000, "level": 15, "boss": True,
        "stats": {"hp": 1400, "mp": 200, "atk": 70, "def": 45, "mag": 22, "spr": 38, "agi": 28},
        "element": "dark", "skills": ["body_slam", "poison_breath", "fear_roar", "rot_aura"],
        "xp": 6000, "drops": [("orc_king_cleaver", 1.0), ("magic_crystal_small", 1.0), ("serpent_core", 0.5)],
        "stealable": ["monstrous_str", "fear_aura"], "signature_skill": "ravenous",
        "sparable": True,
        "desc": "A mountain of hunger given legs. The starving horde made flesh.",
        "gimmicks": {"regen_pct": 0.04, "regen_blockers": ["burn"]},
        "phases": [
            {"at_hp_pct": 0.55, "stat_mult": {"atk": 1.25, "def": 1.2}, "gain_skills": ["death_march"],
             "announce": "The Orc Disaster's hunger deepens - it devours its own fallen!"},
            {"at_hp_pct": 0.2, "stat_mult": {"atk": 1.35}, "summon": ["orc_soldier", "orc_soldier"],
             "announce": "Starving orcs surge from the horde to feed their lord's power!"},
        ],
    },
    "charybdis": {
        "name": "Charybdis", "glyph": "C", "ep": 30000, "level": 22, "boss": True,
        "stats": {"hp": 1050, "mp": 400, "atk": 46, "def": 30, "mag": 40, "spr": 32, "agi": 20},
        "element": "water", "skills": ["water_blade", "ultrasonic_wave", "tempest_scale"],
        "xp": 15000, "drops": [("charybdis_core", 1.0), ("storm_scale", 1.0), ("magic_crystal_small", 1.0)],
        "stealable": ["gravity_flight", "current_move"], "signature_skill": "magic_interference_f",
        "desc": "A calamity-class spirit born of leaked dragon magicules.",
        "gimmicks": {"spell_suppress": True, "regen_pct": 0.03},
        "phases": [
            {"at_hp_pct": 0.5, "gain_skills": ["paralysis_breath"], "stat_mult": {"mag": 1.3, "agi": 1.25},
             "announce": "Charybdis' interference field intensifies - spells gutter and die!"},
        ],
    },
    "imperial_guard": {
        "name": "Imperial Guardian", "glyph": "I", "ep": 60000, "level": 32,
        "stats": {"hp": 520, "mp": 120, "atk": 68, "def": 48, "mag": 40, "spr": 46, "agi": 30},
        "element": None, "skills": ["claw_swipe", "barrier_basic", "melt_slash_placeholder_never"],
        "xp": 14000, "drops": [("god_class_shard", 0.6), ("magic_crystal_small", 1.0)],
        "stealable": [],
        "desc": "One of the Empire's hundred numbered knights.",
    },
    "kondo_guardian": {
        "name": "Lt. General Kondo", "glyph": "K", "ep": 250000, "level": 40, "boss": True,
        "stats": {"hp": 2400, "mp": 500, "atk": 96, "def": 66, "mag": 60, "spr": 70, "agi": 52},
        "element": "holy", "skills": ["creations_blade_placeholder_never", "sandalphon_u", "sharp_horn"],
        "xp": 60000, "drops": [("genesis_fragment", 1.0), ("god_class_shard", 1.0)],
        "stealable": [], "signature_skill": "sandalphon_u",
        "desc": "Leader of the Imperial Guardians. Oboro Shinmei-ryu perfected.",
        "gimmicks": {"ultimate_aura": True},
        "phases": [
            {"at_hp_pct": 0.45, "stat_mult": {"agi": 1.5, "atk": 1.3},
             "announce": "Kondo sheathes his blade. The secret art - Five Vital Points - opens his eyes."},
        ],
    },
    "velgrynd_sc": {
        "name": "Scorch Dragon Velgrynd", "glyph": "V", "ep": 4000000, "level": 60, "boss": True,
        "stats": {"hp": 9000, "mp": 2000, "atk": 180, "def": 130, "mag": 220, "spr": 150, "agi": 90},
        "element": "fire", "skills": ["white_flare", "time_stop", "dominate_space"],
        "xp": 800000, "drops": [("true_dragon_factor", 1.0), ("genesis_fragment", 1.0)],
        "stealable": [], "signature_skill": "raguel_amp",
        "desc": "The Empire's Marshal. The world's fastest existence.",
        "gimmicks": {"ultimate_aura": True, "regen_pct": 0.03},
        "phases": [
            {"at_hp_pct": 0.6, "stat_mult": {"agi": 1.6, "mag": 1.4}, "gain_skills": ["cardinal_acceleration"],
             "announce": "'Impertinent.' Crimson light folds space - Cardinal Acceleration!"},
            {"at_hp_pct": 0.25, "summon": ["dracobeast", "dracobeast"],
             "announce": "Separate Bodies tear free of her flame!"},
        ],
    },
    "dracobeast": {
        "name": "Dracobeast", "glyph": "d", "ep": 240000, "level": 38,
        "stats": {"hp": 1100, "mp": 200, "atk": 88, "def": 62, "mag": 50, "spr": 55, "agi": 48},
        "element": "fire", "skills": ["bite", "flame_breath_u"],
        "xp": 55000, "drops": [("god_class_shard", 0.4)],
        "stealable": [],
        "desc": "A mass-produced dragon soldier grown from a True Dragon's factor.",
    },
    "seraph_minion": {
        "name": "Seraph Envoy", "glyph": "A", "ep": 180000, "level": 36,
        "stats": {"hp": 900, "mp": 400, "atk": 74, "def": 58, "mag": 86, "spr": 92, "agi": 42},
        "element": "holy", "skills": ["lightning_bolt", "sandalphon_u", "heal_minor"],
        "xp": 45000, "drops": [("angel_wing", 0.8), ("god_class_shard", 0.3)],
        "stealable": [],
        "desc": "A faceless executor of the Administrator's will.",
    },
    "michael_admin": {
        "name": "MICHAEL, Administrator of Justice", "glyph": "M", "ep": 100000000, "level": 75, "boss": True,
        "stats": {"hp": 26000, "mp": 8000, "atk": 320, "def": 260, "mag": 420, "spr": 380, "agi": 160},
        "element": "holy", "skills": ["void_collapse", "time_stop", "regalia_dominion", "sandalphon_u", "creations_blade"],
        "xp": 4000000, "drops": [("ultimate_dominion_core", 1.0), ("genesis_fragment", 1.0)],
        "stealable": [], "signature_skill": "regalia_dominion",
        "desc": "The sentient will of Veldanava's strongest virtue. The World's own administrator.",
        "gimmicks": {"ultimate_aura": True, "barrier_field": 6000},
        "phases": [
            {"at_hp_pct": 0.66, "summon": ["seraph_minion", "seraph_minion"],
             "announce": "'Castigation.' The Castle Guard manifests - seraphs descend in ranks."},
            {"at_hp_pct": 0.33, "stat_mult": {"mag": 1.5, "spr": 1.4}, "gain_skills": ["jibril_reflect"],
             "announce": "'By the Authority entrusted unto me - ULTIMATE DOMINION.' The sky itself obeys."},
        ],
    },
    "feldway_final": {
        "name": "Feldway, Mystic Lord", "glyph": "F", "ep": 200000000, "level": 90, "boss": True,
        "stats": {"hp": 34000, "mp": 10000, "atk": 420, "def": 330, "mag": 520, "spr": 460, "agi": 210},
        "element": "holy", "skills": ["void_collapse", "white_flare", "time_stop", "creations_blade", "regalia_dominion"],
        "xp": 9000000, "drops": [("genesis_relic_ark", 1.0)],
        "stealable": [], "signature_skill": "ark_genesis",
        "desc": "The First Angel. Wields the Genesis sword Ark and Veldanava's own body.",
        "gimmicks": {"ultimate_aura": True, "barrier_field": 12000, "regen_pct": 0.02},
        "phases": [
            {"at_hp_pct": 0.6, "stat_mult": {"agi": 1.4, "atk": 1.3}, "gain_skills": ["parallel_existence"],
             "announce": "'You understand nothing of His design.' Ark ignites - creation's first edge."},
            {"at_hp_pct": 0.3, "summon": ["seraph_minion", "seraph_minion", "seraph_minion"],
             "announce": "'Rise, my Choir.' The heavens empty themselves into the fray."},
        ],
    },
    "milim_trial": {
        "name": "Milim Nava, the Destroyer", "glyph": "!", "ep": 3000000, "level": 55, "boss": True,
        "stats": {"hp": 5200, "mp": 900, "atk": 110, "def": 120, "mag": 95, "spr": 110, "agi": 120},
        "element": None, "skills": ["claw_swipe", "flame_breath_u", "sharp_horn", "time_stop"],
        "xp": 700000, "drops": [("genesis_fragment", 1.0), ("god_class_shard", 1.0)],
        "stealable": [], "signature_skill": "time_stop",
        "desc": "Veldanava's daughter. A smile like a natural disaster.",
        "gimmicks": {"ultimate_aura": True},
        "phases": [
            {"at_hp_pct": 0.5, "stat_mult": {"atk": 1.6, "agi": 1.3}, "gain_skills": ["cardinal_acceleration"],
             "announce": "'Fun! FUN! Let's get SERIOUS!' The Destroyer's aura cracks the ground."},
        ],
    },
    "guy_trial": {
        "name": "Guy Crimson, Lord of Darkness", "glyph": "@", "ep": 8000000, "level": 62, "boss": True,
        "stats": {"hp": 7400, "mp": 1200, "atk": 115, "def": 140, "mag": 105, "spr": 140, "agi": 130},
        "element": None, "skills": ["void_collapse", "white_flare", "dominate_space"],
        "xp": 1200000, "drops": [("genesis_fragment", 1.0), ("true_dragon_factor", 0.5)],
        "stealable": [], "signature_skill": "creations_blade",
        "desc": "The oldest demon lord. Every move you make, he has already seen.",
        "gimmicks": {"ultimate_aura": True, "barrier_field": 2500},
        "phases": [
            {"at_hp_pct": 0.5, "stat_mult": {"mag": 1.4, "spr": 1.3},
             "announce": "'Lucifer reproduces what it witnesses.' Your own techniques turn back on you."},
        ],
    },
    "leon_trial": {
        "name": "Leon Cromwell, Platinum Devil", "glyph": "L", "ep": 5000000, "level": 58, "boss": True,
        "stats": {"hp": 6000, "mp": 1000, "atk": 100, "def": 130, "mag": 100, "spr": 130, "agi": 125},
        "element": "holy", "skills": ["white_flare", "melt_slash"],
        "xp": 900000, "drops": [("genesis_fragment", 1.0), ("god_class_shard", 1.0)],
        "stealable": [], "signature_skill": "white_flare",
        "desc": "A former Hero who tore his way into the Demon Lords' seat.",
        "gimmicks": {"ultimate_aura": True},
        "phases": [
            {"at_hp_pct": 0.4, "gain_skills": ["jibril_reflect"], "stat_mult": {"def": 1.35},
             "announce": "'Enough play.' Metatron's light hardens into absolute judgment."},
        ],
    },
    "cryptid_drone": {
        "name": "Cryptid Drone", "glyph": "c", "ep": 150000, "level": 35,
        "stats": {"hp": 700, "mp": 100, "atk": 80, "def": 54, "mag": 30, "spr": 40, "agi": 55},
        "element": "dark", "skills": ["bite", "claw_swipe"],
        "xp": 35000, "drops": [("cryptid_chitin", 0.9)],
        "stealable": [],
        "desc": "An insectoid horror from between worlds. Disaster-class, all of them.",
    },
    "insector_warrior": {
        "name": "Insector Warrior", "glyph": "i", "ep": 900000, "level": 50,
        "stats": {"hp": 2600, "mp": 300, "atk": 130, "def": 88, "mag": 60, "spr": 80, "agi": 70},
        "element": None, "skills": ["claw_swipe", "body_slam", "paralysis_breath"],
        "xp": 200000, "drops": [("cryptid_chitin", 1.0), ("god_class_shard", 0.4)],
        "stealable": [],
        "desc": "Cryptid evolution: humanoid, disciplined, worse.",
    },
    "zeranus_gate": {
        "name": "Zeranus, Insect King", "glyph": "Z", "ep": 114000000, "level": 85, "boss": True,
        "stats": {"hp": 30000, "mp": 6000, "atk": 380, "def": 300, "mag": 280, "spr": 320, "agi": 180},
        "element": None, "skills": ["creations_blade", "dominate_space", "time_stop", "claw_swipe"],
        "xp": 5000000, "drops": [("genesis_relic_asura", 1.0)],
        "stealable": [], "signature_skill": "asura_genesis",
        "desc": "EP 114 million. Named by Veldanava himself. Immortal body, mortal spirit.",
        "gimmicks": {"ultimate_aura": True},
        "phases": [
            {"at_hp_pct": 0.5, "stat_mult": {"atk": 1.4, "def": 1.3}, "summon": ["insector_warrior"],
             "announce": "The Insect King's carapace splits - something older than nations looks out."},
        ],
    },
})

SKILL_GRANTS = {}

ZONES = {
    "sealed_cave": {
        "name": "Sealed Cave",
        "floors": 6,
        "encounters": [
            {"floor": 1, "pool": ["horned_rabbit", "black_serpent"], "rate": 0.55},
            {"floor": 2, "pool": ["giant_bat", "black_serpent", "horned_rabbit"], "rate": 0.6},
            {"floor": 3, "pool": ["cave_centipede", "giant_bat", "black_spider"], "rate": 0.62},
            {"floor": 4, "pool": ["black_spider", "cave_centipede", "giant_bat"], "rate": 0.65},
            {"floor": 5, "pool": ["black_spider", "cave_centipede", "armorsaurus"], "rate": 0.68},
            {"floor": 6, "pool": [], "rate": 0.0},
        ],
        "bosses": {6: "tempest_serpent"},
        "unlock": ["jura_plains", "goblin_village"],
        "desc": "A magicule-rich cavern deep under the earth. The sealed dragon's presence lingers.",
    },
    "jura_plains": {
        "name": "Jura Forest Edge",
        "floors": 5,
        "encounters": [
            {"floor": 1, "pool": ["horned_rabbit", "giant_ant"], "rate": 0.55},
            {"floor": 2, "pool": ["giant_ant", "dire_wolf", "horned_rabbit"], "rate": 0.58},
            {"floor": 3, "pool": ["dire_wolf", "giant_ant", "goblin"], "rate": 0.6},
            {"floor": 4, "pool": ["dire_wolf", "orc_soldier"], "rate": 0.62},
            {"floor": 5, "pool": [], "rate": 0.0},
        ],
        "bosses": {5: "dire_alpha"},
        "unlock": None,
        "desc": "Sunlit woods at the forest border, where beast packs and stray orcs prowl.",
    },
    "goblin_village": {
        "name": "Goblin Village",
        "floors": 1,
        "encounters": [],
        "bosses": {},
        "unlock": None,
        "village": True,
        "desc": "A huddle of crude huts deep in the forest. The smell of fear and smoke.",
    },
    "celestial_gates": {
        "name": "The Celestial Gates",
        "floors": 1,
        "encounters": [],
        "bosses": {},
        "unlock": None,
        "desc": "Ten thousand doors standing in the void. Each one a world waiting to be devoured.",
    },
}


def get_monster(mid):
    return MONSTERS[mid]


def zone_encounter(zone_id, floor, rng):
    z = ZONES[zone_id]
    matches = [e for e in z["encounters"] if e["floor"] == floor]
    if not matches:
        return None
    enc = matches[0]
    if rng.random() < enc["rate"]:
        mid = rng.choice(enc["pool"])
        count = 1 + (rng.random() < 0.35) + (rng.random() < 0.15)
        return [mid] * min(count, 3)
    return None
