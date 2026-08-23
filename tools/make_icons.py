import struct
import zlib


def make_icon(size, path):
    px = []
    r0, g0, b0 = 10, 14, 20
    for y in range(size):
        row = []
        for x in range(size):
            cx, cy = (x - size/2)/(size/2), (y - size/2)/(size/2)
            d = (cx*cx + cy*cy) ** .5
            if d < .62:
                w = (0.62-d)/0.62
                wob = 1 + .08*((x*.13)+(y*.07))
                rr = int(70 + 185*w*wob)
                gg = int(60 + 175*w*wob)
                bb = int(30 + 40*w)
                row.append((min(rr,255), min(gg,255), max(bb,40)))
            elif d < .68:
                row.append((255, 215, 94))
            else:
                row.append((r0, g0, b0))
        px.append(row)

    raw = b"".join(b"\x00" + bytes(v for p in r for v in p) for r in px)

    def chunk(tag, data):
        c = struct.pack(">I", len(data)) + tag + data
        return c + struct.pack(">I", zlib.crc32(tag + data) & 0xffffffff)

    ihdr = struct.pack(">IIBBBBB", size, size, 8, 2, 0, 0, 0)
    png = (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
           + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b""))
    open(path, "wb").write(png)


make_icon(192, "web/icon192.png")
make_icon(512, "web/icon512.png")
print("icons written")
