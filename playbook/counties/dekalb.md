# DeKalb County

Deliverables: legal description, plat map, zoning. No tax page. PIN: 10 digits `TT-SS-BBB-PPP` (`08-00-000-000`), entered unhyphenated in the viewer and the recorder search.

Domains: spatial.dekalbcounty.org (COMPASS parcel viewer, tax map PDFs, community development viewer), lrs.dekalbrecorder.com (Land Records Search) and imagesite-prod.azurewebsites.net (its deed image viewer), plus municipal zoning sites. Beware DeKalb County, Georgia (its GIS shows up first in searches).

Work like a person at the PC (`RULES.md`, "Browse like a person").

## Parcel lookup (the county test)

**Open** the county's COMPASS viewer, `https://spatial.dekalbcounty.org/compass/welcome.asp`, **type** the address (house number and street, no suffix) in its search and **click** the match. Several rows for one house number (condos, duplexes): pick the exact one; ambiguous is UNCERTAIN_MATCH. **Read** the parcel panel: PIN (parcel number), situs address (the whole line, `100 MAIN ST ANYTOWN, IL 60000`), tax map page (for example `8-1A`) and its link, county zoning code, special use, acreage, where it shows them. **Municipality:** the viewer's corporate limits or the situs town; a zoning code of `INC` means incorporated (the county does not zone it), anything else means unincorporated.

Record with `fetch.py county --county DEKALB --pin <PIN> --muni "<municipality or UNINCORPORATED>"`; add `--lon --lat` only if the viewer shows the parcel's coordinates.

## Legal description (Land Records Search, the same Land-Code system as Kane)

1. **Open** `https://lrs.dekalbrecorder.com/search?searchPin=<pin10>` (the site's own PIN search), wait about 8 s. One row per document: DOC NUM, view icon, DATE FILED, TYPE, GRANTOR, GRANTEE, SUB BLOCK LOT (`0000/0000/0000` with the subdivision name under it), SEC/TWP/R.
2. Newest conveyance: `A1 - WD`, `A3 - QCD`, `A5 - Trs Deed` and the other `A` deed types. Skip `F2 - Mtg`, `J1 - RELEASE`, `J2 - PTL RELEASE` and other liens.
3. **Open the image** with a scripted click, as on Kane (a real click on the view icon only raises a tooltip): **run script** to click the view link in that row. Wait about 9 s for the DOCUMENT IMAGE modal (served from imagesite-prod.azurewebsites.net).
4. Make the viewer top level: **run script** `location.href = document.getElementById('image_iframe').src` (the token is single-session: read it from the page). Wait about 9 s. If the viewer's domain is refused: DOMAIN_REFUSED with imagesite-prod.azurewebsites.net.
5. The viewer is "TiffEditorUi" (Kane uses the same one): run the rAF patch, wait about 4 s, then capture the legal exactly as in `counties/kane.md` step 5 (the viewer's own Download or Print if it has one, otherwise zoom with its own control and capture). Frame from the "Permanent Index Number" line through the end of the legal paragraph (on a typical DeKalb deed the PIN, "Commonly Known As" address and legal are all on page 1; tested 2026-10 on a quitclaim deed). For page 2, use the page selector in the top toolbar.

Free, watermarked Unofficial. Never buy.

## Plat map (tax map page PDF)

1. `python fetch/fetch.py now`, then **click** the tax map page link in the parcel panel (it is `https://spatial.dekalbcounty.org/map-pages/<page>.pdf`, a plain document; opening it downloads it). `python fetch/fetch.py grab-download --since <epoch> --name ".pdf" --dest "_data\_scratch\mappage.pdf"`.
2. Page 1 is the aerial version; **page 2 is the line version with the dimensions** (vector, with a text layer). Sheets are 792 x 1224 pt at 1" = 200'. Render page 2 per `recipes/pdf-sheets.md` (`--pages 2`).
3. Find the subject: the lot number and the parcel suffix sit together (for example lot `12` and `-005`), the block number is in an oval (for example `300`), street names are printed. The same parcel suffix appears several times on every sheet (one per block): take the one next to the lot number, inside the right block, near the street name.
4. At 1" = 200' a residential lot is only about 4 x 6 pt and the dimension text is tiny: the crop is about 60 to 90 pt square, so it needs a very high dpi (about `2400 * 72 / crop width in pt`, roughly 2000; see `recipes/pdf-sheets.md` for sheets that large). `stitch.py crop` it. Checks per `deliverables/plat-map.md`.

## Zoning

* **Unincorporated:** the parcel panel's county zoning code is the district (A-1, RC-1, PDR and others); a special use flag and the Chapter 53 code link sit with it. Image: the county's community development viewer, `https://spatial.dekalbcounty.org/vertigisstudio/web/?app=9aa6e557bf3441938d8d224b3a5cd849`: search the address, **click** the parcel, capture with the zoning legend. Say "unincorporated DeKalb County zoning".
* **Incorporated:** `INC` means the county does not zone it; never report INC. **City of DeKalb** (tested): the city's zoning map viewer (search the web for "City of DeKalb zoning map"); the popup gives the zoning code and notes with PD ordinance numbers, and the map draws its own district colours with a Legend. Zoom so the parcel and house numbers read, capture map and legend, compose with the ring at the pin (`recipes/municipal-zoning.md`). Sycamore: the city's parcel-based zoning map. Others (Genoa, Sandwich, Hinckley, Malta, Cortland and more): `recipes/municipal-zoning.md`.

Capture and caption per `deliverables/zoning.md`.

## Run log facts

`<legal in short> | <deed type> <doc> rec <date> | map page <page> (rev <date>); printed <dims> = <sf>` and anything unreconciled.
