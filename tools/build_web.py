import shutil
from pathlib import Path

root = Path(".")
docs = root / "docs"
if docs.exists():
    shutil.rmtree(docs)
docs.mkdir()
for f in ["index.html", "manifest.webmanifest", "icon192.png", "icon512.png", "files.json"]:
    shutil.copy2(root / "web" / f, docs / f)
print("docs/ built for GitHub Pages")
