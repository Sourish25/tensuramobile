# TENSURA: PATH OF THE REINCARNATED — GAME DESIGN DOC
Python console RPG · turn-based · grind-to-godhood · deep kingdom sim

## PILLARS
1. Every kill matters: devour -> steal skills/materials/forms (Predator core).
2. Mastery by use: skills level 0-100%, unlock upgrades, combine into new skills.
3. Your strength lifts others: naming spends life force, subordinates evolve tiers.
4. Kingdom = second character: districts/jobs/economy/diplomacy feed power back.
5. The ceiling never comes: post-god dimensional grinding forever.

## PLAYER CREATION - STARTING RACES
| Race | Intrinsics | Fantasy | Evolution line |
|---|---|---|---|
| Slime | Absorb, Dissolve, Self-Regeneration | balanced devourer | Slime->Named Slime->Demon Slime->Ultimate Slime->True Dragon-tier->God-tier |
| Goblin | Night Vision, Vigor | weak but fastest recruit synergy | Goblin->Hobgoblin->Hobgoblin Elite->Goblin King->Ogre Mage-tier->Oni King |
| Lizardman | Scale Body, Swim | warrior | Lizardman->Dragonewt->Dragon Warrior->Dragon Lord-tier->Storm Dragon-blooded |
| Ogre | Monstrous Strength, Fear Aura | slow glass cannon | Ogre->Kijin->Oni->Awakened Oni->Flame General-tier |
| Direwolf | Scent Track, Sprint | speed/agility | Direwolf->Tempest Wolf->Star Wolf->Divine Wolf->Sky Raptor-tier |

Each race seeds ONE latent unique skill (awakens at level milestones): Sage-analyst / Leader-command / Tyrant-blade / Berserker-rage / Predator-hunt flavor.

## STATS
HP vitality. MP magicules (= life force; spent by naming; restored by rest/devour/time). ATK physical power. DEF guard. MAG spellpower. SPR spirit/holy resist. AGI turn order. LUK drop/crit.
EP = computed power index (stats + skills + mastery). Rank letters from EP:
F / E / D / C / B / A / Special A (100k+) / S (~400k) / Special S (800k+) / Million Class (1M+).

## SKILLS
Tiers: Intrinsic (racial) -> Common -> Extra -> Unique -> Ultimate (+Manas).
- Mastery 0-100% gained by combat use; thresholds 25/50/75/100 grant upgrade ranks (Fireball -> Hellflare).
- Combination recipes (master both parents -> forge child): Water Blade+Water Pressure=Control Water; Control Flame+Dark Flame=Hellflare; Sticky Thread+Steel Thread=Sticky Steel Thread; Shadow Motion+Replication=Thousand Shadow Death; Analyze+Parallel Operation=Auto-Battle Mode.
- Only ultimates counter ultimates: enemy ultimate aura suppresses lower-tier skills unless you hold one.
- Unique awakening: milestone events. Ultimate: Demon Lord awakening + soul threshold + boss absorption.

## PREDATOR SYSTEM (central)
Post-victory Devour roll: skill-steal chance scales with (yourLv - enemyLv) + LUK; bosses guarantee their signature skill.
Stomach: timeless storage (corpses/materials/loot). Analysis converts stored data into skills/craftable items (instant with analyst uniques, timed otherwise).
Mimicry: equip absorbed forms for stat multipliers + form intrinsics; 3-turn combat switch cooldown.
Isolate: neutralize incoming harm/status into MP refund.
Upgrade path: Glutton (Rot/Receive/Provide) -> Belzebuth (Soul Consume, Food Chain) -> Azathoth (Soul Glutton, Complex Space).

## COMBAT
Speed-sorted rounds. Party up to 4 active (hero + subordinates), bench swaps between rounds.
Commands: Attack / Skill / Guard / Item / Form (mimicry) / Flee. Mid-combat Consume vs foes under 15% HP once Belzebuth unlocked.
Status effects: burn, poison, paralysis, charm, fear, bind, seal (skill-lock), soul damage (bypasses regen), curse (conditional auto-death).
Elements: fire/water/wind/earth/lightning/holy/dark. Holy runs on spirit particles and pierces barriers.
Barrier fields block spells until broken; Magic Interference fields cut spellpower 90%.
Boss gimmicks: phases, living-core dependency, corpse-rebuild regen (countered by burn/core isolation), loyalty-funded absolute defense, once-per-day nukes, bait clones.

## NAMING & SUBORDINATES
Spare defeated monsters or meet wanderers -> Name them: costs % of max MP (species-dependent); target evolves one species tier and joins your roster.
Roster assignment: Active Party (max 4) / Kingdom Job (worker output scales with their stats) / Dungeon Garrison / Bench.
Food Chain (later): gift mastered skills to soul-linked subordinates; their growth feeds back a small % to you.
Ally stances: Aggressive / Balanced / Defensive / Support.

## KINGDOM SIM (deep Tempest)
Districts: Central Plaza / Residential / Industrial / Agricultural / Commercial / Hot Spring / Labyrinth Gate / Highway Gate / Research Academy.
Buildings per district; construction costs days + gold + materials + laborers. Effects: passive income/day, crafting unlocks, recruit pool quality, population growth, party buffs, system unlocks (Forge -> crafting; Dungeon Gate -> floor income; Academy -> research; Barrier Works -> city defense; Embassy -> diplomacy actions).
Population per race, happiness, workforce allocation across jobs (farm/smith/guard/builder/research/service), unemployment penalty.
Economy: tax slider (happiness tradeoff), treasury, trade routes unlocked via diplomacy (Dwargon arms-for-magicore, Blumund potions, Farmus food, Church truce, Guild card integration).
Diplomacy: relation meters -100..+100 per faction; envoy/gift/treaty/trade/threat actions; low relations trigger invasion events.
Events: festival (+happiness/population), tournament (arena battles, champion joins Big Four), plague, caravan, monster migration, human-nation siege (defense battle), Walpurgis summons.
City defense rating vs raid strength; losing a siege damages districts instead of ending the run.

## PROGRESSION ARC
P0 Cave Awakening (tutorial cave, F-E): mobs, sealed Dragon event, absorb basics.
P1 Village Era (E-C): goblin village, first names, wolf pack boss, hot spring discovery.
P2 Dwargon & Founding (C-B): dwarf city trade, found Tempest, first districts, lizardman alliance trial, Orc Lord invasion defense.
P3 Calamity Trials (B-A): Charybdis-class spawns, tournament arena, Church duel trial, soul harvest begins.
P4 Demon Lord Awakening (A to Special A): soul threshold met -> evolution cascade to ALL named allies, unique-to-ultimate upgrades, Octagram seat.
P5 Octagram Era (Special A-S): rival lord trials gauntlet, labyrinth public opening economy.
P6 Empire War (S-Special S): labyrinth defense waves, Imperial Guardian duels, True Dragon-tier fights.
P7 Angelic Interference (Special S+): Administrator raid, seize ultimate dominion.
P8 GODHOOD: creation tier unlocks.
P9 Post-God infinite: Dimensional Gates (procedural worlds w/ scaling modifiers), Genesis relic hunts x7, endless labyrinth deepening, successor training, World Recreator prestige reset with permanent bonuses.

## PRESENTATION
ANSI 256-color, box-drawing panels, block HP bars, ASCII monster glyphs, ASCII title logo.
Voice of the World styled announcements: <<World Language>> Confirmed. Skill [X] acquired.
Great Sage assistant persona answers: Received. / Understood. / Question. / Report.
Saves: JSON in saves/, autosave on transitions, 3 slots.

## ARCHITECTURE
game.py entry point.
src/core: ui.py (render/input), save.py, rng.py.
src/data: skills.py, monsters.py, items.py, races.py, buildings.py, zones.py.
src/entities: unit.py (combatant base), player.py, subordinate.py.
src/systems: combat.py, predator.py, skills_sys.py, naming.py, kingdom.py, progression.py, voice.py.
src/screens: title.py, char_create.py, hub.py, dungeon.py, kingdom_screen.py, post_god.py.
