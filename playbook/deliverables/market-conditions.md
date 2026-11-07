# Market conditions PDF: `market-conditions-<slug>.pdf`

Every address. It is built from the eight market graphs (`deliverables/market-graphs.md`) and runs right after them in the `market` procedure.

Example: `Workfiles\100-W-Main-St-Anytown-IL\market-conditions-100-W-Main-St-Anytown-IL.pdf`.

## 1. The data

The narrative needs the monthly values behind the charts, not just the latest month in the value panel. Infosparks draws with Highcharts, so read each series while its chart is open. Define this once with **run script**, after the `__pick` helper from the graph spec:

```js
window.__vals = {};
window.__series = () => { const w = document.getElementById('ifs').contentWindow;
  const c = w.Highcharts.charts.filter(Boolean).slice(-1)[0]; const s = c.series[0];
  window.__vals[window.__title()] = s.data.map(p => Math.round(p.y * 1000) / 1000);
  return window.__title() + ' ' + s.data.length; };
```

Call `window.__series()` right after each `__pick` (it returns the title and the point count, 45 for a three-year view ending in September). At the end read them back one or two at a time so the output is not truncated, for example `window.__vals['Median Sales Price'].join(',')`. The first point is January three years back, the last is the month in the value panel. % of original price comes back as a fraction (0.986 is 98.6 %). Check the last value of each series against the value panel in its capture.

If the graphs were already done on an earlier run and only the PDF is missing, do not capture again: open Infosparks the same way, set the same area and filters the graphs show (read the legend and footnote of `market-median-sale-price-<slug>.png`), and run `__pick` plus `__series` for each graph.

## 2. The narrative

One paragraph, plain and factual, no em or en dashes: the standard market conditions comment. In this order:

1. The trend over the three years in one sentence ("Prices increased from 2023 through mid-2025 and have been stable since.").
2. Median sale price now, the change from the same month a year earlier, and the range it has held in recently when it is flat.
3. Average sale price now and its change from a year earlier.
4. Median price per square foot now and its change from a year earlier (skip for 2 to 4 units, which have no price per sq ft data).
5. Marketing time: median days now against a year earlier and the recent range (say "selling more slowly", "steady" or "selling more quickly" only as the numbers show).
6. Sale price ratio: median % of original list price now, average in parentheses, against the recent range.
7. The conclusion, in the standard sentence: "Prices are currently increasing." (or stable, or declining), then "<Increasing | Stable | Declining> is marked as the market trend at the top of page 1 of the report." Never add "Time adjustments are based on specific differences." That line is for edge cases and the appraiser adds it by hand.

Dates as MM/YYYY. Prices to the dollar as Infosparks shows them, percentages to one decimal. Every figure must come from the series read in step 1; recompute each change yourself rather than trusting a rounded panel figure. Write the paragraph to `_data\_scratch\narrative-<slug>.txt`.

## 3. Build

The graph PNGs are already in the property folder. Then:

```bash
python fetch/tools/market_conditions.py --dir "<folder>" --slug <slug> \
  --area "<area line>" --filters "<filters>" --through "<Month YYYY of the last point>" \
  --narrative-file "_data\_scratch\narrative-<slug>.txt" --out "<folder>\market-conditions-<slug>.pdf"
```

* `--area`: the area the graphs used. A suburb is "Naperville, IL". Chicago is the neighborhood or ZIP in parentheses-city form: "Lincoln Park (Chicago), IL" or "ZIP Code 60614 (Chicago), IL".
* `--filters`: the footnote's filters in the order Property Class, Property Type, Construction Type, Seller Type, for example "Single Family, Detached Single-Family, Resale, Traditional" or "2 to 4 Units, Resale, Traditional".

The tool crops each graph to its chart, lays them out four to a page on legal paper in the fixed order and leaves out any PNG that is not there. It refuses a narrative containing an em or en dash.

## 4. Check and save

Render page 1 (`python fetch/tools/pdf.py render "<folder>\market-conditions-<slug>.pdf" "_data\_scratch\mc-<slug>" --dpi 60 --pages 1`) and look at `_data\_scratch\mc-<slug>-1.png`: the header names the right area and filters, the paragraph reads cleanly, every graph is there and its legend matches the area. The `--out` above already wrote it into the property folder (RULES.md, Saving a file). Then record:

* `--status ok --note "Market conditions PDF: <area>, <trend>"` (for example `"Market conditions PDF: Naperville, stable"`).
* The graphs failed, so there is nothing to build from: `--status failed --reason OTHER --seen "market graphs missing"`; it comes back once the graphs are in.
