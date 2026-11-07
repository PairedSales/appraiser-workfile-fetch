#!/usr/bin/env python3
"""Compose the zoning exhibit: caption band on top, map on the left with a
white-haloed black ring around the subject, map key on the right.
See playbook/deliverables/zoning.md for the standard. Run from the folder root:

  python fetch/tools/zoning_compose.py --map MAP.png --legend KEY.png --ring X Y [--radius 55] \
      --out OUT.png --caption "line 1" "line 2" ["line 3"]

  --ring X Y   subject position in MAP.png pixels (centre of the ring)
  --no-ring    the map already marks the subject unmistakably and a ring would hide it
  --key-below  put the key under the map instead of beside it (very wide maps)
The first caption line is bold: "<address> | PIN <pin> | Zoning: <code> <name>".
"""
import argparse
from PIL import Image, ImageDraw, ImageFont

F = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except OSError:
        return ImageFont.load_default(size=size)


ap = argparse.ArgumentParser()
ap.add_argument("--map", required=True)
ap.add_argument("--legend", required=True)
ap.add_argument("--ring", nargs=2, type=int)
ap.add_argument("--radius", type=int, default=55)
ap.add_argument("--no-ring", action="store_true")
ap.add_argument("--key-below", action="store_true")
ap.add_argument("--caption", nargs="+", required=True)
ap.add_argument("--out", required=True)
a = ap.parse_args()

m = Image.open(a.map).convert("RGB")
k = Image.open(a.legend).convert("RGB")
if not a.no_ring:
    if not a.ring:
        raise SystemExit("--ring X Y is required unless --no-ring")
    px, py = a.ring
    d = ImageDraw.Draw(m)
    r = a.radius
    for w, c in ((9, "white"), (4, "black")):
        d.ellipse((px - r, py - r, px + r, py + r), outline=c, width=w)

f, fb = font(F, 22), font(FB, 24)
pad, lh = 14, 32
W = max(m.width, k.width) if a.key_below else m.width + pad + k.width


def wrap(text, fnt, width):
    """Split a caption line into lines that fit the exhibit width."""
    words, lines, cur = text.split(" "), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if fnt.getlength(t) <= width or not cur:
            cur = t
        else:
            lines.append(cur)
            cur = w
    lines.append(cur)
    return lines


rows = []
for i, t in enumerate(a.caption):
    for ln in wrap(t, fb if i == 0 else f, W - 2 * pad):
        rows.append((ln, fb if i == 0 else f))
ch = pad * 2 + lh * len(rows)
if a.key_below:
    o = Image.new("RGB", (W, ch + m.height + pad + k.height), "white")
    o.paste(m, (0, ch))
    o.paste(k, (0, ch + m.height + pad))
else:
    o = Image.new("RGB", (W, ch + max(m.height, k.height)), "white")
    o.paste(m, (0, ch))
    o.paste(k, (m.width + pad, ch))
dd = ImageDraw.Draw(o)
for i, (t, fnt) in enumerate(rows):
    dd.text((pad, pad + i * lh), t, fill="black", font=fnt)
dd.line((0, ch - 2, o.width, ch - 2), fill="black", width=2)
o.save(a.out)
print("saved %s %dx%d" % (a.out, o.width, o.height))
