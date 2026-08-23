import sys
sys.path.insert(0, ".")
sys.path.insert(0, "tools")
from src.entities.unit import Player
from src.data.skills import get_skill

hero = Player("Dbg", "slime")
hero.level = 17
for _ in range(16):
    hero.gain_xp(hero.xp_to_next())
    hero.level_up()
    hero.check_evolution()
print("skills:", sorted(hero.skills.keys()))
usable = [sid for sid in hero.skills
          if (get_skill(sid) or {}).get("kind") in ("attack", "support", "defense")]
print("usable:", usable)
for sid in usable:
    s = get_skill(sid)
    print(f"  {s['name']} MP:{s.get('mp',0)} power:{s.get('power')} kind:{s['kind']}")
