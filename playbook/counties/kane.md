# Kane County

Deliverables: legal description, plat map, zoning. No tax page (ignore the tax figures the viewer shows). PIN: 10 digits `TT-SS-BBB-PPP`; the tax map prints only `BBB-PPP`.

Domains: gistech.countyofkane.org (GIS viewer, tax map PDFs), lrs.kanecountyrecorder.net (Land Records Search), imagesite-prod.azurewebsites.net (the deed image viewer itself: easy to miss; it was imagesite-kane-prod.land-code.com before October 2026), plus municipal zoning sites. No Kane host is reachable from a shell.

Work like a person at the PC (`RULES.md`, "Browse like a person"). Two tabs: one on gistech (lookup, plat), one that starts on LRS and becomes the image viewer.

## Parcel lookup (the county test)

**Open** the county's GIS parcel viewer on gistech.countyofkane.org, **type** the address in its search box and **click** the match. **Read** the parcel panel: PIN, site address and city, municipality, township, use, and the last deed's document number and date where it shows them. The county's site addresses often run street names together (`MAPLEWOOD` for Maple Wood): search the house number plus the first few letters of the street with no suffix before concluding the address is not in Kane. Ambiguous is UNCERTAIN_MATCH. Municipality blank or unincorporated means the County zones it. The deed number shown is the one you should find at the top of the LRS list.

With a PIN already in hand, `https://gistech.countyofkane.org/gisIMS/KaneMap/getTaxMaps.html?txtSearch=<pin10>` is the county's own tax map page for it (used for the plat).

Record with `fetch.py county --county KANE --pin <PIN> --muni "<municipality or UNINCORPORATED>"`; add `--lon --lat` only if the viewer shows the parcel's coordinates.

## Legal description (Land Records Search)

1. **Open** `https://lrs.kanecountyrecorder.net/search?searchPin=<pin10>` (the site's own PIN search), wait about 8 s. One row per document: DOC NUM, view icon, DATE FILED, TYPE, GRANTOR, GRANTEE, SUB BLOCK LOT (`<subdivision code> <unit>/<block>/<lot>`, for example `SUBDCODE 2/NONE/12` = Unit 2, no block, Lot 12; the SUBDIVISION CODES menu decodes the code), SEC/TOWN/RANGE.
2. Newest conveyance: `WD`, `QC`/`QCD`, `TD`, `SWD`, `EXD`. Skip `MTG`, `REL`, `MOD`, `SUBA`; a `TOD` is worth a note, not the vesting deed. Cross-check against the deed number the viewer showed. Numbers look like `96K000000` (before 2000) or `2013K000000`.
3. **Open the image.** A real click on the view icon raises a tooltip and a second click closes what opened, so this step uses a scripted click: **run script** to click the view link in that row. Wait about 9 s for the DOCUMENT IMAGE modal.
4. **Make the viewer top-level.** The modal's iframe is cross-origin and takes no input: **run script** `location.href = document.getElementById('image_iframe').src` (the token is single-session, read it from the page). Wait about 9 s. Since October 2026 the viewer is the same "TiffEditorUi" as DeKalb's, on `imagesite-prod.azurewebsites.net`. A permission error here means your browser tool has not been allowed on that domain: DOMAIN_REFUSED.
5. **Capture the legal.** If the page stays blank, run the rAF patch (`recipes/browser.md`) and wait about 4 s. If the viewer has its own Download or Print control, use it (`python fetch/fetch.py now`, **click** it, `grab-download --name ".pdf" --dest "_data\_scratch\deed.pdf"`, then render and crop per `recipes/pdf-sheets.md`). Otherwise zoom with the viewer's own zoom control until the text is crisp, hide the toolbar and side panels, **hover** off, and **capture** from the grantor paragraph through the PIN and address lines and any "subject to" paragraph that belongs with them; more than one screen is `recipes/tiled-capture.md`. For page 2 use the viewer's page selector. Tested on a single-family warranty deed: the legal sat on page 1, from about 43 % to 74 % of the way down.

Free, watermarked Unofficial. Never buy.

## Plat map (LinePrint tax map PDF)

1. **Open** `https://gistech.countyofkane.org/gisIMS/KaneMap/getTaxMaps.html?txtSearch=<pin10>` and **read** the sheet links it lists (never assume the year). Use a **LinePrint** (clean vector, 300 to 600 KB), not the Composite (aerial, about 10 MB). Sheets come as the township overview (1"=1200'), the section (1"=400') and quarter-section enlargements (1"=100'): take the largest scale listed.
2. `python fetch/fetch.py now`, **click** the LinePrint link (it downloads), `python fetch/fetch.py grab-download --since <epoch> --name ".pdf" --dest "_data\_scratch\taxmap.pdf"`. `python fetch/tools/pdf.py text` confirms the PIN's `BBB-PPP` label is on the sheet; if not, try the next sheet listed. A parcel straddling two enlargements: the sheet where the label sits furthest from the edge.
3. Render and crop per `recipes/pdf-sheets.md`. Sheets are 1224 x 1368 pt. At 1"=100', 72 pt is 100 ft: aim for a 250 to 350 ft crop (about 180 to 250 pt) at a long edge of about 2100 px, so about 700 dpi. Put the block number and the subdivision name in frame when they are near. Tested on an old-town single-family lot: a quarter-section sheet (1"=100', 2025), a crop about 215 x 175 pt at 700 dpi (2100 x 1700).
4. Checks per `deliverables/plat-map.md`: every side dimensioned, the lot number matching the deed (ignore sub-2-ft chords; cul-de-sac frontages print `R=60` with an arc), printed area against any lot area the viewer shows. Old-town GIS areas run about 2 % large: note a difference that size rather than reconcile it. `getMapLegend.html?mappage=<sheet>` on the same site shows the legend and scale bar if needed.

## Zoning

* **Unincorporated:** the county zones it. The county Zone Atlas (`kanecountyil.gov/FDER/Pages/development/zoneatlas/`) is the adopted map; the county's zoning web map (search the web for "Kane County zoning map") identifies the district (E-1, F, R-1 and others), any special use and petitions. It covers unincorporated land only. Note any special use. Say "unincorporated Kane County zoning".
* **St. Charles:** the city's zoning map viewer (search the web for "St. Charles IL zoning map"); its popup gives the code, description and a link into the code.
* **Geneva** (tested): its colours are by broad type (Residential, Business...), so the code must come from an identify popup. **Open** the city's "My Place" web map, `https://www.arcgis.com/apps/mapviewer/index.html?webmap=f0f7804ef6c24d7cb3714ea901ffd30e`, **type** the address in its search, turn on its hidden "Zoning Districts" layer in the Layers panel (**click** the eye icon), **click** the parcel: the popup pages through Parcel (PIN, address) and Zoning District (Zone Code, Description). A second zoning hit of HI is the historic district overlay, worth its own line. **Capture** the clean map with the pin, the Legend's Zoning Districts block and both popups, and stack the key and popups in the right column (`python fetch/tools/stitch.py vstack`). District names: Geneva City Code Title 11 (D-SFMR = Single-Family Medium Density Residential, Sec 11-4A-6).
* **Proven before:** North Aurora (village parcel map flags PUD), Carpentersville (2024 zoning map), Elgin (city zoning app).
* **Anyone else** (Elgin, Aurora, Batavia, South Elgin, Sugar Grove...): `recipes/municipal-zoning.md`. Kane County's own ArcGIS org is `gistsn`; beware Kane County, Utah.

Capture and caption per `deliverables/zoning.md`.

## Run log facts

`<legal in short> | <deed type> <doc> rec <date> | sheet <LinePrint> (<year>); printed <dims> = <sf>` and anything unreconciled.
