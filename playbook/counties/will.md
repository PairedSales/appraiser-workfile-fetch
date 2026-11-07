# Will County

Deliverables: property card, plat map, zoning. **No recorded legal description** (the Will County Recorder offers no free document images; treat Will like Lake). No tax page: the assessor property card replaces it and carries the assessor's legal description. PIN: 16 digits `TT-TT-SS-BBB-PPP-UUUU` (for example `11-00-00-000-000-0000`); the tax map prints the block (`BBB`) and parcel (`-PPP`). Never buy documents.

Domains: www.willcountysoa.com (assessor property search and card), gis.willcountyillinois.com (the county's GIS map viewer and tax map), plus municipal zoning sites.

Map viewers paint through rAF: run the rAF patch (`recipes/browser.md`) after every navigation.

## Parcel lookup (the county test)

1. **Open** `https://www.willcountysoa.com/PINSearch` and use the site's property search by address (house number and street name, no directional or suffix). With the PIN already known, fill the six PIN boxes instead (**type** into each, or one **run script** that sets their values if the boxes will not take typing) and **click** Search.
2. Several hits (same street in two towns): keep the one whose city or ZIP matches. No hit: try fewer letters of the street name. The card often spells or formats the street differently from the address as given (for example `MAPLE DR (PVT)` on the card, `Maple Circle` as given): match on house number, town and the map, then work by PIN.
3. Go on to the property card: its Legal Description is the abbreviated legal for `fetch.py county --abbrev-legal`, and its lot number is the one to find on the plat map.

**Municipality:** in the county GIS viewer, the municipal boundaries layer at the subject (or the county zoning layer, which shows "Municipal" for incorporated land). No municipality means unincorporated.

Point for zoning and the flood map: the middle of the subject lot, read from the county viewer if it shows coordinates for a clicked point, otherwise from any public web map that does.

## Property card (willcountysoa.com)

Tested 2026-10-25 on a new construction card (no building data) and on one with full building data.

1. From the search results (`/PINSearchResults`), **click** the PIN link. It opens the card in a new tab: work in that tab and close the results tab so no stray tab is left. No result row: the PIN is wrong or not yet in the assessor file; record NOT_FOUND with what the page said.
2. Wait about 3 s; the URL is `/PRC/<code>` (the code is per session, do not reuse it). **Read text** and note: township, owner, street address, subdivision, property class, the Assessment rows, Sale Information, Building Information, Legal Description.
3. **Print it** (`deliverables/tax-page.md`, "Printing the page"): **run script** to hide the page buttons (Prev Parcel, Next Parcel, View Tax Map, Property Search Portal) and set `document.title = 'Property card <PIN> <address>'`, then print. Then `python fetch/fetch.py grab-download ... --dest "<folder>\property-card-<slug>.pdf" --trim-blank` (the card leaves a trailing blank page that `--trim-blank` removes). Tested 2026-10-31: one letter page, county header through the Legal Description.
4. Fallback only if the print does not land: capture the card per `recipes/html-capture.md` (it is about 1085 x 1270 CSS px, so it goes in tiles), `fetch.py put` as `property-card-<slug>.png`.
5. Cross-checks per `deliverables/property-card.md`; anything worth the appraiser's attention goes to `fetch.py note`.

Building data is the township assessor's and only as current as their last upload; the card says so in red.

## Plat map (the county tax map)

1. Reach the county tax map at the subject: the card's View Tax Map button (before hiding the buttons), or the county's GIS map viewer on gis.willcountyillinois.com with the tax map layers on, searched by PIN or address. (Not yet tested in this form: record what each route showed.)
2. Zoom with the page's own controls until the dimensions, lot numbers and parcel numbers draw (they draw at any residential scale on the county tax map). Centre the subject. Lot lines are thin and grey; that is how the county draws them.
3. Hide panels and clutter (**run script**), **hover** off, **capture** the subject lot, one parcel deep on every side and the nearest street name; for more area at a legible zoom, `recipes/tiled-capture.md`.
4. If the route hands over a PDF tax map sheet instead, follow `recipes/pdf-sheets.md`.

Checks (`deliverables/plat-map.md`): every printed side readable; the subject's parcel number (`-PPP`) and block (`BBB`) inside the crop; the lot number matches the card's Legal Description. Printed frontage x depth against the card's or viewer's lot area; a mismatch is a `fetch.py note` with both figures.

## Zoning

* **Unincorporated:** the county zoning layer is parcel based (it shows the last approved zoning and case number for each PIN). In the county viewer, turn on the zoning layer and its legend with the tax map lines on top, search the subject, **click** it to read the district, **capture** map and legend, compose with the ring at the subject. Districts: A-1 agricultural, A-2 rural residence, E-1, E-2 estate, R-1 to R-5 single family, R-6 multi-family, C-1 to C-6 commercial, I-1 to I-3 industrial; an `s` suffix in the legend marks special use. Say "Unincorporated Will County".
* **Incorporated** (the county layer shows "Municipal"): the municipality's own zoning map or viewer via `recipes/municipal-zoning.md` (Joliet, Bolingbrook, Romeoville, Plainfield, Lockport, New Lenox, Mokena, Frankfort, Homer Glen, Shorewood, Naperville's Will County part, and others).

Capture and caption per `deliverables/zoning.md`.

## Run log facts

`Lot <n> (tax map block <BBB>), <municipality or unincorporated> | printed <dims> = <sf>` and anything unreconciled. Then the property card's line from `deliverables/property-card.md`. fetch.py adds the abbreviated legal when there is one and states that no recorded legal exists.
