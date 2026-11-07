# McHenry County

Deliverables: plat map (the county GIS dimension map; McHenry has no plat or tax map sheet, the file keeps the `-plat-map` name), zoning, tax page. **No recorded legal description**: the Recorder offers no free images; do not look for one. The assessor's abbreviated legal goes to `fetch.py county --abbrev-legal`. PIN: 10 digits; Athena wants it hyphenated (`19-00-000-000`), the tax site URL unhyphenated. Never buy documents.

Domains: www.mchenrycountygis.org (Athena map viewer), mchenryil.devnetwedge.com (tax page), www.arcgis.com (Map Viewer for municipal zoning), plus municipal zoning sites. If a site is refused, retry once after about 10 s (sites have refused for a few minutes and then worked).

Athena and Map Viewer paint through rAF: run the rAF patch (`recipes/browser.md`) after every navigation.

## Parcel lookup (the county test)

1. **Open** `https://mchenryil.devnetwedge.com/`. **Click** the Address Search tab (by coordinate; **find** can miss it), **type** the house number in House Number (Low) and one distinctive street word in Street Name (no suffix), Search.
2. Keep only rows whose house number is exactly the subject's. Several towns: pick the subject's city (Crystal Lake and Lakewood addresses mix). Nothing: try another spelling of the street word. **Click** the match.
3. **Read text**: Parcel Number, Site Address, Property Class, Township, the taxing districts (a city or village among them means it is incorporated; none means unincorporated), Legal Description, Sales History (deed document numbers).

The tax page can spell the street differently from GIS (`100 MAPEL` vs `100 MAPLE LN`): confirm with the PIN. Abbreviated legal: the tax page's form (spaced, `DOC 2022R0000000 PT LT 4 SAMPLE SUB`), verbatim.

Point for zoning and the flood map: the subject's latitude and longitude from Athena's results panel for the parcel (step 2 of the plat map), or the middle of the lot read from the map.

**Companion parcels.** On the Athena map, look at the lots touching the subject that have no site address (often class 0030 vacant). **Click** one and check its tax page Sales History for the subject's deed document number. A second PIN on the same deed is usually part of the site: include it in the plat map and add a `fetch.py note` with its legal, area and tax.

## Plat map (Athena with Parcel Text)

Coordinates below are from a 1469-wide screenshot (tested 2026-10); expect them to shift on another window size.

1. **Open** `https://www.mchenrycountygis.org/athena/?noDisclaimer=true` (the county's own link that skips the splash; the tax site's `&parcel=` link does not zoom, ignore it). rAF patch, wait about 5 s.
2. **Click** the search box at the top centre (it says "Enter parcel", about (720, 31)), **type** the hyphenated PIN, **click** SEARCH (about (873, 31)), wait about 5 s. The parcel is highlighted cyan and a RESULTS panel opens. **Read text** of the panel: parcel area, latitude and longitude.
3. MAP LAYERS panel: **click** **Parcel Text** (first button, about (98, 127)); it turns pale when on. Wait about 3 s.
4. Close MAP LAYERS (its x, about (160, 88)) and RESULTS (its x, about (445, 693)); take a **screenshot** to confirm both are gone.
5. Zoom with the mouse wheel **centred on the subject**: scroll up 3 ticks, wait 5 s, 2 more if the slider is not at the top (the `+` greys out at maximum). Grey blurry blocks mean the rAF patch is missing.
6. Find the subject (cyan fill, its parcel number suffix, lot number in red). **Hover** off the map, a small **screenshot**, then **capture** the whole subject, any companion parcel, one parcel of context each side and a street name. A full-window Athena capture can time out: capture only the needed region, or tile it (`recipes/tiled-capture.md`). No caption: the highlight identifies the subject.
7. Checks: list every printed figure (magenta on the subject side, cyan on neighbours; labels at a sharp corner can wrap, `21.` over `.7` is 21.7). Printed record calls and the drawn lot often differ here: note both, never "fix" the printed figure. A side with no figure (often a private lane) is "not dimensioned". Report the parcel area in sf and acres (the tax site's Acres is often 0.0000); with a companion parcel, the combined area too.

Athena's own Print tool makes a map PDF through its own dialog: not used.

## Zoning

1. **Who zones it:** the taxing districts on the tax page (above), or a municipal boundary layer in Athena if one is listed. No municipality means unincorporated.
2. **The map:** Crystal Lake (proven): the city's zoning layer opened in ArcGIS Map Viewer, map plus Legend panel. The city's own viewer sits behind a terms checkbox: never tick it. Unincorporated: the county's zoning map (proven 2026-10 on an unincorporated parcel; find it among the county GIS maps on www.mchenrycountygis.org). Other towns: `recipes/municipal-zoning.md`.
3. Search the address in the map, turn on the legend, **click** the parcel to read the district, **capture** map and legend, compose with the ring at the subject. Caption line 2: `Subject circled. <Municipality or Unincorporated McHenry County>.`; line 3: `Source: <municipality> zoning map (<layer name>), <viewer>. Captured <date>.` Check the subject's fill against the legend swatch.

Caption per `deliverables/zoning.md`.

## Tax page (devnetwedge)

1. **Open** `https://mchenryil.devnetwedge.com/parcel/view/<pin10>/<year>`, `<year>` = the latest tax year with a bill (the banner "TAXPAYER INFORMATION FOR 2025 PROPERTY TAXES PAYABLE IN 2026" means 2025; the newest year may have no billing yet), or click through from the address search.
2. **Read text**: Parcel Number, Site Address, Property Class, Tax Code, Township, Net Taxable Value, Tax Rate, Total Tax, Legal Description, assessments, billing, exemptions, sales history (deed number, date, price), payment history.
3. Keep only the useful panels: **run script** to hide every panel except Property Information, Assessments, Billing, Exemptions, Sales History and Payment History, hide the photo, scroll to the top.
4. **Print it** (`deliverables/tax-page.md`, "Printing the page") straight after step 3 in the same tab: set `document.title = 'Tax page <PIN> <address>'` and print. Tested 2026-10-31: 2 letter pages, county banner, the six panels, nothing else.
5. Fallback only if the print does not land: capture the tidied page per `recipes/html-capture.md`.

The site's Print Parcel button prints the whole untidied page; step 4 prints the tidied one instead. Never pay or add to a cart.

## Run log facts

`<subdivision and lot> | GIS dims <figures>; parcel area <sf> (<ac> ac) | class <c>, NTV <v>, <year> tax $<amt>` plus companion parcels. fetch.py adds the abbreviated legal.

## Gotchas

Property class `0040` improved residential lot, `0030` vacant residential lot (county codes, not Cook's).
