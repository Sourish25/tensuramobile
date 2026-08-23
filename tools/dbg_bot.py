import sys
sys.path.insert(0, ".")
sys.path.insert(0, "tools")
from playthrough import make_battle_bot
from src.entities.unit import Player

hero = Player("Dbg", "slime")
hero.level = 17
for _ in range(16):
    hero.gain_xp(hero.xp_to_next())
    hero.level_up()
    hero.check_evolution()
hero.learn_skill("icicle_lance", mastery=25)
hero.learn_skill("steel_thread", mastery=40)
hero.learn_skill("sticky_thread", mastery=30)
state = {"hero": hero}
bot = make_battle_bot(state)
acts = ["Auto: OFF", "Attack", "Skill", "Guard", "Item", "Flee"]
ci = bot("SimRim's turn - command:", acts)
print("cmd pick:", ci, "->", acts[ci])
usable = [
    "Sticky Thread [extra] MP:4 30% (Adept)",
    "Steel Thread [extra] MP:6 40% (Adept)",
    "Icicle Lance [extra] MP:5 25% (Novice)",
    "Wind Cutter [extra] MP:5 25% (Novice)",
]
si = bot("Use which skill?", usable)
print("skill pick:", si, "->", usable[si])
