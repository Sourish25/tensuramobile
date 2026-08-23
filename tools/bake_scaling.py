from pathlib import Path
import re

p = Path(r"src\data\monsters.py")
s = p.read_text(encoding="utf-8")


def bake(block_name, factor):
    global s
    pat = re.compile(r'("%s": \{.*?"stats": )\{([^}]*)\}' % block_name, re.S)
    m = pat.search(s)
    assert m, block_name
    body = m.group(2)

    def bump(mm):
        k, v = mm.group(1), int(mm.group(2))
        return f"{k}{max(1, int(v * factor))}"

    new = re.sub(r'(\w+":\s*)(\d+)', bump, body)
    s = s[:m.start(2)] + new + s[m.end(2):]


for name, lvl in [("black_serpent", 1), ("cave_centipede", 2), ("black_spider", 3), ("giant_bat", 2),
                  ("horned_rabbit", 1), ("giant_ant", 2), ("dire_wolf", 3), ("goblin", 1),
                  ("armorsaurus", 8), ("tempest_serpent", 12), ("orc_soldier", 6), ("orc_general", 9),
                  ("mercenary", 8), ("holy_knight", 11), ("dire_alpha", 10), ("orc_rider", 7)]:
    bake(name, round(1 + (lvl - 1) * 0.12, 2))

p.write_text(s, encoding="utf-8")
print("baked legacy scaling into early templates")
