import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from webify import webify_all

root = Path(".")
docs = root / "docs"
if docs.exists():
    shutil.rmtree(docs)
docs.mkdir()
for f in ["index.html", "manifest.webmanifest", "icon192.png", "icon512.png", "files.json", ".nojekyll"]:
    shutil.copy2(root / "web" / f, docs / f)

webified = webify_all(root)

game_root = docs / "game"
game_root.mkdir(exist_ok=True)
for f in json.loads((root / "web" / "files.json").read_text(encoding="utf-8")):
    dst = game_root / f
    dst.parent.mkdir(parents=True, exist_ok=True)
    if f.endswith(".py") and f in webified:
        dst.write_text(webified[f], encoding="utf-8")
    else:
        shutil.copy2(root / f, dst)
print("docs/ built: site + webified game payload")
