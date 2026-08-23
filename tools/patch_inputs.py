from pathlib import Path

repl = [
    ("src/systems/combat.py",
     'input(ui.R + "Not enough MP. Enter to pick again." + ui.RESET)',
     'ui.pause(ui.R + "Not enough MP. Pick again." + ui.RESET)'),
    ("src/systems/combat.py",
     'input(ui.R + "No items. " + ui.RESET)',
     'ui.pause(ui.R + "No items." + ui.RESET)'),
    ("src/screens/hub.py",
     'input(ui.R + "Not enough gold." + ui.RESET)',
     'ui.pause(ui.R + "Not enough gold." + ui.RESET)'),
    ("src/screens/title.py",
     'input(ui.R + "Empty or corrupted slot." + ui.RESET)',
     'ui.pause(ui.R + "Empty or corrupted slot." + ui.RESET)'),
]

for fname, old, new in repl:
    p = Path(fname)
    s = p.read_text(encoding="utf-8")
    if old in s:
        s = s.replace(old, new)
        p.write_text(s, encoding="utf-8")
        print("patched", fname)
    else:
        print("MISS", fname, old[:40])
