import zipfile, re, os, html
from pathlib import Path

SRC = Path(r"C:\Users\Sourish\Desktop\games\Tensura\EPUB")
DST = Path(r"C:\Users\Sourish\Desktop\games\Tensura\novels_txt")
DST.mkdir(exist_ok=True)

def epub_to_text(epub_path: Path, out_path: Path):
    with zipfile.ZipFile(epub_path) as z:
        names = [n for n in z.namelist() if n.lower().endswith((".xhtml", ".html", ".htm"))]
        # order by natural sort of path so chapters come out in reading order
        def key(n):
            m = re.findall(r"\d+", n)
            return (n.count("/"), int(m[-1]) if m else 0, n)
        names.sort(key=key)
        parts = []
        for n in names:
            try:
                raw = z.read(n).decode("utf-8", errors="ignore")
            except Exception:
                continue
            raw = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", raw, flags=re.S | re.I)
            raw = re.sub(r"<br\s*/?>", "\n", raw, flags=re.I)
            raw = re.sub(r"</(p|div|h[1-6]|li|blockquote)>", "\n", raw, flags=re.I)
            txt = re.sub(r"<[^>]+>", "", raw)
            txt = html.unescape(txt)
            txt = re.sub(r"[ \t\xa0]+", " ", txt)
            txt = re.sub(r"\n\s*\n+", "\n\n", txt).strip()
            if len(txt) > 200:
                parts.append(txt)
    out_path.write_text("\n\n".join(parts), encoding="utf-8")
    return out_path.stat().st_size

for epub in sorted(SRC.glob("*.epub")):
    vol = re.search(r"LN (\d+)", epub.name).group(1)
    out = DST / f"vol_{int(vol):02d}.txt"
    size = epub_to_text(epub, out)
    print(f"{out.name}: {size/1024:.0f} KB")
