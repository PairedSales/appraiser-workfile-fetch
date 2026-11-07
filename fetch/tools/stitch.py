#!/usr/bin/env python3
"""Stitch capture tiles back into one image. Run from the folder root:
    python fetch/tools/stitch.py ...

Grid (plat maps, rendered PDFs, map exports):
  python fetch/tools/stitch.py grid --tile TW TH --out OUT.png [--crop W H] 0,0=t00.png 1,0=t10.png 0,1=t01.png ...
  Each tile is resized back to exactly TW x TH (zoom captures come back scaled by the
  display ratio), pasted at (col*TW, row*TH), and the result is cropped to W x H
  (the true canvas size) when --crop is given.

Vertical stack (tax pages, long web pages captured in panel-boundary tiles):
  python fetch/tools/stitch.py vstack --out OUT.png t1.png t2.png ...
  Tiles are scaled to the width of the first one and stacked top to bottom.

Page (HTML pages captured with recipes/html-capture.md: edge tiles are smaller, never resized):
  python fetch/tools/stitch.py page --tile 900 --out OUT.png 0,0=t00.png 1,0=t10.png 0,1=t01.png ...
  Each tile is pasted as captured at (col*900, row*900), then the result is trimmed to the
  non-white area plus 10 px.

Crop (cut a region out of a full-window screenshot):
  python fetch/tools/stitch.py crop IN.png OUT.png X0 Y0 X1 Y1
  Coordinates are pixels of IN.png.

Preview (half size copy to look at before shipping):
  python fetch/tools/stitch.py preview IN.png OUT.png
"""
import sys
from PIL import Image


def grid(args):
    tw = th = None
    out = crop = None
    tiles = {}
    i = 0
    while i < len(args):
        a = args[i]
        if a == "--tile":
            tw, th = int(args[i + 1]), int(args[i + 2]); i += 3; continue
        if a == "--out":
            out = args[i + 1]; i += 2; continue
        if a == "--crop":
            crop = (int(args[i + 1]), int(args[i + 2])); i += 3; continue
        cr, path = a.split("=", 1)
        c, r = (int(x) for x in cr.split(","))
        tiles[(c, r)] = path
        i += 1
    cols = max(c for c, _ in tiles) + 1
    rows = max(r for _, r in tiles) + 1
    img = Image.new("RGB", (cols * tw, rows * th), "white")
    for (c, r), p in tiles.items():
        img.paste(Image.open(p).convert("RGB").resize((tw, th), Image.LANCZOS), (c * tw, r * th))
    if crop:
        img = img.crop((0, 0, min(crop[0], img.width), min(crop[1], img.height)))
    img.save(out)
    print("saved %s %dx%d" % (out, img.width, img.height))


def vstack(args):
    out = args[args.index("--out") + 1]
    paths = [a for a in args if a not in ("--out", out)]
    ims = [Image.open(p).convert("RGB") for p in paths]
    w = ims[0].width
    ims = [im if im.width == w else im.resize((w, round(im.height * w / im.width)), Image.LANCZOS) for im in ims]
    img = Image.new("RGB", (w, sum(im.height for im in ims)), "white")
    y = 0
    for im in ims:
        img.paste(im, (0, y)); y += im.height
    img.save(out)
    print("saved %s %dx%d" % (out, img.width, img.height))


def page(args):
    from PIL import ImageChops
    t = 900
    out = None
    tiles = {}
    i = 0
    while i < len(args):
        a = args[i]
        if a == "--tile":
            t = int(args[i + 1]); i += 2; continue
        if a == "--out":
            out = args[i + 1]; i += 2; continue
        cr, path = a.split("=", 1)
        c, r = (int(x) for x in cr.split(","))
        tiles[(c, r)] = Image.open(path).convert("RGB")
        i += 1
    W = max(c * t + im.width for (c, r), im in tiles.items())
    H = max(r * t + im.height for (c, r), im in tiles.items())
    img = Image.new("RGB", (W, H), "white")
    for (c, r), im in sorted(tiles.items(), key=lambda x: (x[0][1], x[0][0])):
        img.paste(im, (c * t, r * t))
    bb = ImageChops.difference(img, Image.new("RGB", img.size, "white")).getbbox()
    if bb:
        img = img.crop((max(0, bb[0] - 10), max(0, bb[1] - 10), min(W, bb[2] + 10), min(H, bb[3] + 10)))
    img.save(out)
    print("saved %s %dx%d" % (out, img.width, img.height))


def preview(args):
    im = Image.open(args[0])
    im.resize((max(1, im.width // 2), max(1, im.height // 2)), Image.LANCZOS).save(args[1])
    print("saved", args[1])


def crop(args):
    im = Image.open(args[0])
    x0, y0, x1, y1 = (int(v) for v in args[2:6])
    im.crop((x0, y0, x1, y1)).save(args[1])
    print("saved", args[1], "%dx%d" % (x1 - x0, y1 - y0))


if __name__ == "__main__":
    {"grid": grid, "vstack": vstack, "page": page, "crop": crop, "preview": preview}[sys.argv[1]](sys.argv[2:])
