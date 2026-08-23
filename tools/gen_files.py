import json
from pathlib import Path

root = Path(".")
files = ["game.py", "game_web.py"]
for sub in ("src",):
    for p in sorted((root / sub).rglob("*.py")):
        if p.name == "__pycache__":
            continue
        files.append(p.as_posix())
for p in sorted((root / "web").iterdir()):
    if p.suffix in (".html", ".webmanifest", ".png", ".js") and p.name != "files.json":
        pass
out = {"files": files}
Path("web/files.json").write_text(json.dumps(files, indent=1), encoding="utf-8")
print(json.dumps(files, indent=1))
