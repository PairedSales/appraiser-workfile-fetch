#!/usr/bin/env python3
"""PDF helper (replaces poppler's pdftotext / pdftoppm, which Windows does not have).

    python fetch/tools/pdf.py text   FILE.pdf [--pages N]              print the text of the first N pages (default all)
    python fetch/tools/pdf.py render FILE.pdf OUT_PREFIX [--dpi 300] [--pages 1-2] [--clip X0 Y0 X1 Y1]
                                                         write OUT_PREFIX-1.png, OUT_PREFIX-2.png, ...
                                                         --clip renders only that region, in PDF points
                                                         from the top left (see info), so a small area of a
                                                         big sheet can be rendered at a high dpi
    python fetch/tools/pdf.py info   FILE.pdf                          page count and page sizes in points

Needs PyMuPDF (pip install pymupdf).
"""
import argparse
import sys

try:
    import pymupdf as fitz  # PyMuPDF
except ImportError:
    import fitz


def page_range(spec, n):
    if not spec:
        return range(n)
    a, _, b = spec.partition("-")
    lo = int(a) - 1
    hi = int(b) if b else lo + 1
    return range(max(lo, 0), min(hi, n))


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    t = sub.add_parser("text"); t.add_argument("pdf"); t.add_argument("--pages", type=int)
    r = sub.add_parser("render"); r.add_argument("pdf"); r.add_argument("out_prefix")
    r.add_argument("--dpi", type=int, default=300); r.add_argument("--pages")
    r.add_argument("--clip", type=float, nargs=4, metavar=("X0", "Y0", "X1", "Y1"))
    i = sub.add_parser("info"); i.add_argument("pdf")
    a = ap.parse_args()
    with fitz.open(a.pdf) as d:
        if a.cmd == "text":
            n = d.page_count if not a.pages else min(a.pages, d.page_count)
            sys.stdout.write("\n".join(d[k].get_text() for k in range(n)))
        elif a.cmd == "render":
            for k in page_range(a.pages, d.page_count):
                out = "%s-%d.png" % (a.out_prefix, k + 1)
                clip = fitz.Rect(*a.clip) if a.clip else None
                pm = d[k].get_pixmap(dpi=a.dpi, clip=clip)
                pm.save(out)
                print(out, "%dx%d" % (pm.width, pm.height))
        else:
            print("pages:", d.page_count)
            for k in range(d.page_count):
                print(k + 1, round(d[k].rect.width), "x", round(d[k].rect.height), "pt")


if __name__ == "__main__":
    main()
