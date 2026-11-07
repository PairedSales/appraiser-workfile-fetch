# Market graphs: eight Infosparks PNGs

Every address. The average and the median of four indicators for the property's city (Chicago: its neighborhood), saved in the property folder:

| Button | Setting | Chart title to confirm | File |
|---|---|---|---|
| Sales Price | MEDIAN | Median Sales Price | `market-median-sale-price-<slug>.png` |
| Sales Price | AVERAGE | Average Sales Price | `market-average-sale-price-<slug>.png` |
| Price Per Sq Ft | MEDIAN | Median Price Per Square Foot | `market-median-price-per-sq-ft-<slug>.png` |
| Price Per Sq Ft | AVERAGE | Average Price Per Square Foot | `market-average-price-per-sq-ft-<slug>.png` |
| Market Time | MEDIAN | Median Market Time | `market-median-market-time-<slug>.png` |
| Market Time | AVERAGE | Average Market Time | `market-average-market-time-<slug>.png` |
| % Orig List (Closed) | MEDIAN | Median Percent of Original Price | `market-median-pct-orig-list-price-<slug>.png` |
| % Orig List (Closed) | AVERAGE | Average Percent of Original Price | `market-average-pct-orig-list-price-<slug>.png` |

All eight are expected; if the plan lists only some (a partial set from an earlier run), capture only those. Older folders may hold the previous names `-market-price-per-sq-ft.png`, `-market-time.png`, `-market-pct-orig-list-price.png`: leave them alone, they are not part of the set.

**2 to 4 units.** Infosparks has no price per sq ft graphs for 2 to 4 unit areas. When the subject is a 2 to 4 unit building (county record or MLS listing), pass `--units <n>` to `python fetch/fetch.py county` or `python fetch/fetch.py record` and save the other six. fetch.py then does not expect the two price per sq ft files.

Domains: connectmls.mredllc.com, connectmls2.mredllc.com, mred.stats.10kresearch.com. Never type credentials: a login form is LOGIN_WALL. Viewing only: do not click Print, Share, Profile, My Areas, Reports or MarketView, do not save an area, and leave the time settings as they open (Line, 3 Years, 12 Months).

**Market conditions PDF.** Every address also gets `market-conditions-<slug>.pdf`, built from these graphs (`deliverables/market-conditions.md`). When the plan lists it, read each chart's data with `__series` right after its `__pick`, so Infosparks does not have to be opened twice.

**Reuse within a run.** If an earlier address in the same run used the same area and the same filters, copy its eight images under this slug instead of capturing again.

## Steps

The images are 1484 x 735: the Infosparks page laid out in a 1484 x 863 viewport (what the old 1500 x 950 window gave), cropped from 45 to 780 px down (area tab, filters, chart, value panel and footnote; no page header and no metric buttons). The Chrome window is usually minimized at night, so a **resize** does not change the viewport and a full-width capture times out. Instead the page runs inside a 1484 x 863 iframe and is captured in two halves. Never resize the window for this.

1. **Open** `https://connectmls.mredllc.com/ssologin.jsp` (signs in from the existing session, lands on connectMLS home), then to `https://connectmls2.mredllc.com/integration/launchTheThing.jsp` (the home page's Infosparks link; it lands on mred.stats.10kresearch.com/stats/market in the same tab).
2. **The frame.** On that page, **run script**:

```js
document.documentElement.style.cssText = 'margin:0;padding:0;overflow:hidden;background:#fff';
Array.from(document.body.children).forEach(e => e.style.display = 'none');
const f = document.createElement('iframe'); f.id = 'ifs'; f.src = '/stats/market';
f.style.cssText = 'position:fixed;left:0;top:0;width:1484px;height:863px;border:0;display:block;z-index:2147483647;background:#fff';
document.body.appendChild(f);
window.__shift = dx => { f.style.left = (-dx) + 'px'; return f.style.left; };
'ok'
```

   Wait about 8 s. Then **run script** `document.getElementById('ifs').contentWindow.dispatchEvent(new Event('resize'))` and wait 3 s (the chart sizes itself to the frame on resize).
3. **Area.** The area box (top left, about (225, 63) for its arrow) opens on "Entire MLS Area". **Click** the arrow, **click** into the field (about (110, 64)), **type** the city, wait 3 s and **click** the suggestion tagged CITY (the first one, about (64, 100), when it is the city; never a subdivision, agent or office). Chicago: use the neighborhood the MLS listing shows (the Chicago zoning identify panel's Community Area is a good source); no match means use Chicago and add `Market: used city, neighborhood not found` to the note.
4. **Filters** with **run script** inside the frame (clicking the label's `div.main` selects it):

```js
const d = document.getElementById('ifs').contentDocument;
const pick = t => { const e = Array.from(d.querySelectorAll('li div.main')).find(x => x.textContent.trim() === t);
  if (!e) return t + ': none'; if (e.closest('li').classList.contains('selected')) return t + ': already'; e.click(); return t + ': clicked'; };
const r = [pick('Detached Single-Family')]; await new Promise(s => setTimeout(s, 2500));
r.push(pick('Resale')); await new Promise(s => setTimeout(s, 2500)); r.push(pick('Traditional')); await new Promise(s => setTimeout(s, 3000));
const foot = Array.from(d.querySelectorAll('*')).filter(e => e.children.length === 0 && /: Traditional/.test(e.textContent)).map(e => e.textContent.trim());
JSON.stringify({r, foot})
```

   Property Class Single Family is already selected; Price Range and Square Footage stay All. Not a detached house: pick the matching Property Type (Attached Single-Family, Townhouse, Condo) or Property Class `2 to 4 Units`. The footnote must read the area then the filters, for example "Naperville: Traditional, Resale, Single Family, Detached Single-Family". Then slide the filter panel one column so it starts at Property Class (as the old captures do): dispatch `mousedown`, `mouseup` and `click` on `d.querySelector('.sliderContainer .buttons.next')`.
5. **The eight charts.** Each metric is an `li.multi` whose first text node is its name (`Sales Price`, `Price Per Sq Ft`, `Market Time`, `% Orig List (Closed)`), with `ul.calcList li` items `Average` and `Median`. Clicking a metric that is not selected selects it on its remembered setting; clicking a `calcList` item of the selected metric switches it. Always confirm from the chart title (an SVG `text` starting "Median " or "Average "), never from the click:

```js
window.__title = () => Array.from(document.getElementById('ifs').contentDocument.querySelectorAll('svg text, svg tspan')).map(e => e.textContent.trim()).find(x => /^(Median|Average) /.test(x));
window.__pick = async (metric, stat) => { const d = document.getElementById('ifs').contentDocument;
  const li = Array.from(d.querySelectorAll('li.multi')).find(l => l.firstChild && l.firstChild.textContent.trim() === metric);
  for (let i = 0; i < 3; i++) { if (li.classList.contains('selected') && (window.__title() || '').startsWith(stat + ' ')) break;
    if (!li.classList.contains('selected')) li.click(); else Array.from(li.querySelectorAll('ul.calcList li')).find(x => x.textContent.trim() === stat).click();
    await new Promise(s => setTimeout(s, 3000)); }
  return window.__title(); };
```

   Define both with **run script**. For each of the eight: **run script** `window.__shift(0); await window.__pick(metric, stat)` (check the title), **capture** region `[0, 45, 782, 780]` at full resolution (the left half, 782 x 735; the result gives the file path and pixel size), then **run script** `window.__shift(702)` and the same **capture** (the right half). **Hover** at a point below the frame (y over 863) before the first capture.
6. **Stitch** each pair in `_data\_scratch\`: the left half whole, then the right half from its column 80 (`782 - 702`) on, pasted at x 782, giving 1484 x 735 (Pillow: `c.paste(A, (0, 0)); c.paste(B.crop((80, 0, 782, 735)), (782, 0))`). Tested on a suburb, 2026-10-13: identical to the old nightly capture except hover highlighting.
7. Save the eight files (`recipes/saving-files.md`) and check each: right title, the intended area in the legend, the intended filters in the footnote, the line reaching the latest month in the value panel. A median % of original price that is a flat 100.0 % line is real data.

If the frame shows a login page, record LOGIN_WALL. Close nothing until the end of the run (`RULES.md`).

## Recording

* `--status ok --note "Market: <area>, <filters>"` (for example `"Market: Naperville, Detached Single-Family Resale Traditional"`).
* Partial: save what came out, then `--status failed --reason OTHER --files "<the missing file names>" --seen "..."`.
* Login form, refused domain, no area match: failed with the reason. Market problems never fail an address.
