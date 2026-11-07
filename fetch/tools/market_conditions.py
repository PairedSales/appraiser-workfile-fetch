"""Build market-conditions-<slug>.pdf from the property's Infosparks graph PNGs.

Run from the folder root (needs Pillow and reportlab, see requirements.txt):

  python fetch/tools/market_conditions.py --dir <folder holding the market-*-<slug>.png files> --slug <slug> \
      --area "ZIP Code 60614 (Chicago), IL" \
      --filters "Single Family, Detached Single-Family, Resale, Traditional" \
      --through "September 2026" --narrative-file narrative.txt --out <path>/market-conditions-<slug>.pdf

Layout (matches the reports made by hand in Oct 2026): legal page, "Market Conditions" title, one line of
area | filters | period, source line, rule, the narrative paragraph, then each graph cropped to the chart
(1484 x 735 PNG cut to x 0-1466, y 240-735), four per page in this order: median and average sale price,
median and average price per sq ft, median and average market time, median and average % of original price.
A graph whose PNG is not there (for example price per sq ft for 2 to 4 units) is left out.
"""
import argparse, os, tempfile
from PIL import Image
from reportlab.lib import colors
from reportlab.lib.pagesizes import legal
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import HRFlowable, Image as RLImage, Paragraph, SimpleDocTemplate, Spacer
from xml.sax.saxutils import escape

ORDER = ["median-sale-price", "average-sale-price", "median-price-per-sq-ft", "average-price-per-sq-ft",
         "median-market-time", "average-market-time", "median-pct-orig-list-price", "average-pct-orig-list-price"]
CROP = (0, 240, 1466, 735)
WIDTH = 489.6

ap = argparse.ArgumentParser()
ap.add_argument("--dir", required=True)
ap.add_argument("--slug", required=True)
ap.add_argument("--area", required=True)
ap.add_argument("--filters", required=True)
ap.add_argument("--through", required=True)
ap.add_argument("--narrative-file", required=True)
ap.add_argument("--out", required=True)
a = ap.parse_args()

narr = open(a.narrative_file, encoding="utf-8").read().strip()
if "\u2014" in narr or "\u2013" in narr:
    raise SystemExit("narrative contains an em or en dash; the report language does not use them")

gray = colors.Color(.333, .333, .333)
title = ParagraphStyle("t", fontName="Helvetica-Bold", fontSize=22, leading=26.4)
sub = ParagraphStyle("s", fontName="Helvetica", fontSize=10, leading=12, textColor=gray)
src = ParagraphStyle("r", fontName="Helvetica-Oblique", fontSize=9, leading=10.8, textColor=gray)
body = ParagraphStyle("b", fontName="Helvetica", fontSize=11, leading=13.2)
sep = "&nbsp;&nbsp;|&nbsp;&nbsp;"

story = [Paragraph("Market Conditions", title), Spacer(1, 4),
         Paragraph(escape(a.area) + sep + escape(a.filters) + sep + "Three-year view through " + escape(a.through), sub),
         Paragraph("Source: MRED connectMLS Infosparks", src), Spacer(1, 4),
         HRFlowable(width="100%", thickness=.75, color=colors.Color(.6, .6, .6), spaceAfter=8),
         Paragraph(escape(narr), body), Spacer(1, 8)]

tmp = tempfile.mkdtemp()
used = []
for n in ORDER:
    p = os.path.join(a.dir, "market-%s-%s.png" % (n, a.slug))
    if not os.path.isfile(p):
        continue
    im = Image.open(p).convert("RGB")
    if im.size != (1484, 735):
        raise SystemExit("%s is %dx%d, expected 1484x735" % (p, im.size[0], im.size[1]))
    c = os.path.join(tmp, n + ".png")
    im.crop(CROP).save(c)
    story += [RLImage(c, width=WIDTH, height=WIDTH * (CROP[3] - CROP[1]) / (CROP[2] - CROP[0])), Spacer(1, 8)]
    used.append(n)
if not used:
    raise SystemExit("no market graph PNGs found in " + a.dir)

SimpleDocTemplate(a.out, pagesize=legal, leftMargin=49.2, rightMargin=49.2, topMargin=40, bottomMargin=40,
                  title="Market Conditions").build(story)
print("ok %s (%d graphs: %s)" % (a.out, len(used), ", ".join(used)))
