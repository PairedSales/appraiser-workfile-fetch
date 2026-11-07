# Cook County

Deliverables: legal description, plat map, zoning, tax page. PIN: 14 digits, `AA-BB-CCC-DDD-EEEE` (block CCC, parcel DDD).

Domains: crs.cookcountyclerkil.gov (recorder, also the parcel lookup), cookcountyil.maps.arcgis.com and maps.cookcountyil.gov (tax maps), www.cookcountypropertyinfo.com (tax portal), gisapps.chicago.gov (Chicago zoning), plus municipal zoning sites.

Work like a person at the PC (`RULES.md`, "Browse like a person"): the site's own search box, its own links and buttons, its own Download control. No server queries.

## Parcel lookup (the county test)

**Recorder search.** **Open** `https://crs.cookcountyclerkil.gov/Search`, **click** **Address/PIN Search** (the centre one of the three search buttons), **click** the search box, **type** the street address without the city (`100 W Main St`), **click** the search button. The results list PIN, Address, City, Zip. Pick the exact match; ambiguous is UNCERTAIN_MATCH. The recorder index tolerates few typos: if nothing comes back, try with and without the directional and the suffix. With a PIN already in hand, **open** `https://crs.cookcountyclerkil.gov/Search/ResultByPin?id1=<14 digits>` (the site's own results page).

**Municipality.** The City column is the postal city, which is not always the municipality. The tax map lookup app (Plat map, step 1) and the town's own zoning map settle it: a parcel the town's map does not cover is probably unincorporated (Zoning, below). Unsure: note it.

Record with `fetch.py county --county COOK --pin <PIN with dashes> --muni "<municipality or UNINCORPORATED>"`. Add `--lon --lat` only if a viewer shows the parcel's coordinates; never look them up by a server query.

## Legal description (Clerk's Recording System)

1. On the PIN's results page, **read text** for the document list (Doc Number, Recorded, Executed, Doc Type).
2. Pick per `deliverables/legal-description.md`: the newest QUIT CLAIM DEED, WARRANTY DEED, TRUSTEE'S DEED or CERTIFICATE OF TITLE (1 to 3 pages, legal on page 1); a MORTGAGE only if there is no deed (legal on the last "EXHIBIT A" page).
3. **Click** the row's **View** link. Document Details: note `# of Pages` and **read** the **Legal Description and Subdivision** panel (Subdiv / Lot / Block / Section / Township / Range) as a cross-check.
4. `python fetch/fetch.py now`, then **click** **View Document in New Window**. With the Chrome setup on, the scanned PDF downloads (free, watermarked UNOFFICIAL COPY). Never add to cart or buy. Then `python fetch/fetch.py grab-download --since <epoch> --name ".pdf" --dest "_data\_scratch\deed.pdf"` (a scan has no text, so match by name).
5. Render and crop per `recipes/pdf-sheets.md`: `python fetch/tools/pdf.py render "_data\_scratch\deed.pdf" "_data\_scratch\deed" --dpi 300`, look at the pages to find the legal (page 1 of a plain deed; an "EXHIBIT A" page when the deed says "legally described on Exhibit A"), then `python fetch/tools/stitch.py crop` from the legal's heading (or the PIN and address lines next to it) through the end of the paragraph. Pages are A4 or letter scans with no text layer. Tested on a single-family executor's deed with the legal on an Exhibit A on page 3: crop x 229 to 2229, y 313 to 1771 at 300 dpi.

## Plat map (tax map PDF)

1. **Sheet.** **Open** the county's tax map lookup app, `https://cookcountyil.maps.arcgis.com/apps/instant/lookup/index.html?appid=ffc0d6133b8b4065adbb990a0bc7c41d`, **type** the address or PIN in its search box, **click** the match and **read** the **Page Letter ID** (the sheet: four digits plus a letter, like `1234A`), and the section, township and municipality where it shows them.
2. **PDF.** **Open** `https://maps.cookcountyil.gov/taxmapviewer/`, find the sheet with the viewer's own search or sheet list, newest year first, and `python fetch/fetch.py now` then **click** its PDF link or Download control. `python fetch/fetch.py grab-download --since <epoch> --name ".pdf" --dest "_data\_scratch\taxmap.pdf"`. Sheets are 11 x 17, 792 x 1224 pt. This site and the tax portal keep a 90 % Chrome zoom: trust the pixel size the capture reports (`recipes/browser.md`).
3. **Find the subject.** Render the sheet (`recipes/pdf-sheets.md`) and look at it. The PIN's 3rd group is the **block number** in an oval (it can repeat around the block), the 4th group is printed in the lot as `-007`, and the **lot number from the legal** sits beside it as a bare number. Always make the lot number cross-check. The map title confirms the section (in the form `E 1/2 NW 1/4 Section <section> - <township> - <range> <TOWNSHIP NAME>`).
4. **Crop.** A typical lot is only 15 to 25 pt by 40 to 60 pt, so render at a high dpi (about `2400 * 72 / crop width in pt`; 720 dpi for a 240 pt wide crop) and `stitch.py crop` it. Keep the crop left of the sheet's notes column (subdivision recording notes run down the right side, about x > 600 pt). Tested on a single-family lot on a 2025 sheet: a crop about 260 x 110 pt at 720 dpi (2600 x 1100 px) took in the lot and the fronting street, and the printed dimensions matched the portal's lot area within 0.1 %.
5. Checks per `deliverables/plat-map.md`; printed frontage x depth against the tax portal's Lot Size (SqFt).

## Zoning

The municipality decides the source.

**Chicago** (`gisapps.chicago.gov/ZoningMapWeb/?liab=1&config=zoning`):
1. **Open** it, wait about 2 s (the search box exists before the app wires it up, so typing too early silently does nothing).
2. **Click** the search box (top left, "Search by Address or PIN #"), **type** the street number and name, **press** Return, wait about 2 s for the pin.
3. **Click directly on the pin or the parcel under it** (a real click). This opens **Identify Results** on the left. **Read** the **Zoning Districts** row (also Landmark District, TIF, ADU Area, Ward, Community Area: the Community Area is the neighborhood for the market graphs). Never read a floating map label.
4. Check the identify panel's address or PIN is the subject's.
5. **Capture** one region holding the Identify Results panel and the pin on the parcel; capture the key at the bottom of the Map Legend panel under "Zoning - Color-Coded"; compose per `deliverables/zoning.md` (or two tiles side by side if they will not fit legibly).

Chicago codes in brief: RS single-unit; RT two-flat, townhouse, multi-unit; RM multi-unit; B business; C commercial; M manufacturing; D downtown; PD planned development (needs the PD ordinance); POS parks; T transportation. The number after the hyphen is the bulk tier.

**South and southwest suburbs** (Alsip and most SSMMA members) share one SSMMA zoning inventory: search the web for the SSMMA or village zoning map viewer, search the address there, **click** the parcel and confirm the popup's PIN is the subject's. Image and key per `recipes/municipal-zoning.md` (the viewer, or the village's adopted map PDF).

**Northbrook**: the village's public "Zoning" web map in Map Viewer, `https://www.arcgis.com/apps/mapviewer/index.html?webmap=c0c6a6c19c274f31ad4900c912c7004b`. **Type** the address in its search, **click** the parcel; the popup gives the district, its description and the zoning document, and the parcel layer's popup the PIN and street address to confirm. It shows house numbers and street names but has no zoning key of its own: take the key from the village's adopted zoning map (`recipes/municipal-zoning.md`), subject's row in bold.

**Proven elsewhere:** Oak Lawn (village zoning map popup shows the PIN), Elgin (city zoning web app identify shows the parcel number), Western Springs, Hanover Park, Des Plaines, Bellwood (2019 adopted map PDF), Dolton, South Holland (SSMMA). Summit's adopted map was not machine-readable: expect a manual retry there.

**Any other municipality:** `recipes/municipal-zoning.md`.

**Unincorporated** (no municipality): the County zones it. Search the web for "Cook County unincorporated zoning map" to find the current official viewer or map, use it the same way, and say "unincorporated Cook County zoning".

## Tax page (Cook County Property Tax Portal)

Needs only the PIN; do it before the plat so Lot Size (SqFt) is in hand.

1. **Open** `https://www.cookcountypropertyinfo.com/default.aspx`. Typing into the five PIN boxes often does not stick: fill them with **run script** (set each box's value and fire its input and change events), then **click** the page's own Search button. Wait about 5 s: the page reads `Property Characteristics for PIN: <PIN>`. (No PIN: the address search on the same page.) The results page is an ASP.NET postback; `pinresults.aspx?pin=` bounces to the search form. An invisible reCAPTCHA has never challenged; if it does, stop and record OTHER.
2. `pinresults.aspx` keeps no state: reloading or navigating away dumps you at the search form. **Read and print before going anywhere else.**
3. **Read text** and keep: property address and township, Assessed Value (with its certification year), Estimated Property Value, Lot Size (SqFt), Building (SqFt), Property Class, Tax Rate, Tax Code, the last two or three billed amounts, and the DOCUMENTS, DEEDS & LIENS list.
4. **Print it** (`deliverables/tax-page.md`, "Printing the page"). Tidy with **run script**: hide everything for print except the PIN heading and `div.accordion`, set the title to `Tax page <PIN> <address>`, then print. The portal's own print stylesheet adds the house photo and a "This printout cannot be used as a tax bill" line, which is fine. Tested 2026-10-31 on a single-family PIN: one letter page with every panel, photo and the disclaimer. This is the last step on `pinresults.aspx`.

   Fallback only if the print does not land: a PNG capture of `div.accordion` (about 985 x 1355 CSS px) from the "Property Characteristics for PIN" heading through the italic disclaimer at the bottom, in bands per `recipes/html-capture.md`, stitched with `python fetch/tools/stitch.py vstack`. A full-window capture times out. Tested: three bands (to the top of "TAX BILLED AMOUNTS", to the top of "REFUNDS AVAILABLE", then the rest) stitched cleanly.
5. Cross-checks per `deliverables/tax-page.md`. The portal's document list often shows only recent documents.

## Run log facts

`<legal in short: Lot, Block, Subdivision> | <deed type> <doc> rec <date> | tax map <page> (<year>); <dims> = <sf> vs portal <sf> | class <c>, AV <v> (<year> cert), est mkt $<v>, bldg <sf> sf, <year> billed $<amt>` and any failed cross-check.

## Gotchas

* Never click Buy Documents, Buy Certified Documents or Add to Cart on CRS. Never buy documents anywhere.
* Condos: the legal references a Declaration and a unit; the tax map shows the condo parcel. The plat is the parcel footprint and the portal's Lot Size is the whole condo parcel: note it.
* Multi-property deeds put each legal on an exhibit page; crop the one for the subject.
* Two PINs on one deed (house plus a side lot) both belong in the notes.
