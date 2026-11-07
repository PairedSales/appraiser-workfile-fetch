# DuPage County

Deliverables: legal description, plat map, zoning. No tax page (deliberately tax free: ignore the tax figures the parcel viewer shows). PIN: 10 digits `TT-SS-BBB-PPP`, entered unhyphenated in the viewer and in the recorder boxes.

Domains: gis.dupageco.org (parcel viewer, county zoning), recorder.dupageco.org (deeds), plus municipal zoning sites. Neither DuPage host is reachable from a shell: everything runs in the browser.

Work like a person at the PC (`RULES.md`, "Browse like a person"). Use two tabs: one on the parcel viewer, one on the recorder.

## Parcel lookup (the county test)

**Open** `https://gis.dupageco.org/parcelViewer/index.html`. It shows a disclaimer modal with an "I agree" checkbox: **do not tick it** (accepting terms is the user's call). Close the modal if it can be closed. If the viewer cannot be used without it, record the item failed with `--needs "open the DuPage parcel viewer in Chrome and accept its disclaimer once"`.

**Type** the address in the viewer's search box (house number and street, `100 MAIN ST`), **click** the match, and **read** the parcel panel: PIN, property address and city, municipality, acreage, property class. Nothing found: drop the directional and the suffix, or search by PIN. Several matches: the exact one; ambiguous is UNCERTAIN_MATCH. The county may index a different street name than the address as given (an address on a two-word street was indexed under the last word only): house number, unit, city and PIN agreeing is enough; note it. Municipality blank or Unincorporated means the County zones it.

Record with `fetch.py county --county DUPAGE --pin <PIN> --muni "<municipality or UNINCORPORATED>"`; add `--lon --lat` only if the viewer shows the parcel's coordinates.

## Legal description (Recorder of Deeds)

**Open** `https://recorder.dupageco.org/Search.aspx`. Postback clicks can leave the tab loading for a long time: if a real **click** on a button hangs, **run script** `setTimeout(() => <that button>.click(), 100)` instead and **read** the result with another **run script** after about 6 s rather than **read text**. A tab that stops answering is wedged: open a new tab and start the search again.

1. **Search by PIN, deeds only.** Coordinate clicks on the four PIN boxes are unreliable: fill them with **run script** (set each value and fire input and change events). Tick the deed types **DEED**, **QUIT CLAIM DEED** and **NR DEED** in the document type list (DuPage has only these three; a warranty deed is DEED), then **click** Search. Wait about 5 s (the URL becomes `Documents.aspx`). The table prints one row per party. The Legal Description column is the county's index (in the form `L 12 B 3 <ABBREVIATED SUBDIVISION> UN 1 <TWP>-<RNG>` = Lot 12, Block 3, <subdivision> Unit 1): confirm the parcel before opening anything. A known document number goes straight to Details through the document number boxes (alpha + 4 digits, `R1971`, and 6 digits).
2. **Open the newest deed:** its document link in the first row (a postback link; the scripted click above is reliable here). `Details.aspx` shows Doc Number, Recording Date, page count and a Legal Description panel with address and PIN: confirm both. It often names the recorded subdivision plat (report its document number and date; do not pull it).
3. **Download the PDF.** `python fetch/fetch.py now`, then **click** **View / Print Document**: it downloads the scan. It intermittently answers 503: wait about 10 s and click again, once. `python fetch/fetch.py grab-download --since <epoch> --name ".pdf" --dest "_data\_scratch\deed.pdf"`.
4. **Crop it** (`recipes/pdf-sheets.md`). Deed pages are scans at about 200 dpi stored one point per scan pixel (page 1 of a tested deed: 1728 x 2277 pt; `python fetch/tools/pdf.py info` shows it), so render at `--dpi 72` to get the scan's own resolution; 300 would only blow it up. Look at page 1, then `python fetch/tools/stitch.py crop` from the deed's heading (or the grantor paragraph) through the "Permanent Index Number" line. Tested on a single-family warranty deed: crop x 100 to 1000, y 45 to 1300 at 72 dpi, trimmed to the heading through the PIN line.

## Plat map (parcel viewer)

On the parcel viewer, with the subject selected, zoom in with the viewer's own controls until the dimension annotation, lot, parcel and block numbers and the yellow PROPERTY ADDRESS callouts draw. They only appear at large scales (finer than about 1:1800), so keep zooming until the figures show. Frame the whole subject lot, one parcel deep on every side and the nearest street name, hide the side panel and other clutter (**run script** if the viewer has no control for it), **hover** off the map and **capture**. Text too small for the area needed: `recipes/tiled-capture.md` (pan with the viewer's own controls and stitch).

The sheet prints the lot depth once for the block and ditto marks (`=`) for repeated widths: that is the county's drafting, not a missing dimension.

Checks per `deliverables/plat-map.md`: all four sides dimensioned and readable, printed frontage x depth against the viewer's acreage (and the municipality's own square footage where its map shows one) within about 1 %. The lot and subdivision must match the deed.

## Zoning

The municipality decides. There is no county-wide map for incorporated land.

* **Naperville**: zoning is on the city's parcel map. Find its public GIS viewer (search the web for "Naperville zoning map"), search the address, **click** the parcel; the popup shows zoning code, description, variance, lot number, subdivision and square footage. Lot number and subdivision matching the deed confirms the parcel.
* **Glen Ellyn**: the village's "Zoning" web map in Map Viewer, `https://www.arcgis.com/apps/mapviewer/index.html?webmap=4abf35a10bfb4ce19b5c18434d394bea`. **Type** the address in its search, **click** the parcel for the district, description and zoning document; zoom so house numbers and the street name show. Key from the map's Legend panel or the village's adopted zoning map (`recipes/municipal-zoning.md`).
* **Other GIS Consortium members** (Roselle, Glendale Heights, Warrenville and others): `recipes/municipal-zoning.md`; most villages publish a "Zoning" web map the same way (search `<village> zoning` on arcgis.com, owner on the village's domain).
* **Unincorporated:** the county's unincorporated zoning map (find it from gis.dupageco.org or by searching the web for "DuPage County unincorporated zoning map"). Search the address, **click** the parcel for the district and its ordinance link, capture with the map's legend. Say "unincorporated DuPage County zoning".
* **Anyone else:** `recipes/municipal-zoning.md`.

Capture and caption per `deliverables/zoning.md`. A PUD suffix gets its one line.

## Run log facts

`<legal in short> (plat rec <date> as Doc <no>) | deed <doc> rec <date> | printed <dims> = <sf>; viewer <ac> ac` and any check that did not reconcile.

## Gotchas

* Never buy documents or certified copies.
* Recorded deeds carry typos (`NORHT`): never correct them silently.
* Condos: the plat is the association's common parcel; note it (the viewer's parcel panel may list the unit PINs).
