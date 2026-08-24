import json
import shutil
from pathlib import Path

root = Path(".")
docs = root / "docs"
if docs.exists():
    shutil.rmtree(docs)
docs.mkdir()
for f in ["index.html", "manifest.webmanifest", "icon192.png", "icon512.png", "files.json", ".nojekyll"]:
    shutil.copy2(root / "web" / f, docs / f)

game_root = docs / "game"
game_root.mkdir(exist_ok=True)
for f in json.loads((root / "web" / "files.json").read_text(encoding="utf-8")):
    src = root / f
    dst = game_root / f
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
print("docs/ built: site + game payload")
