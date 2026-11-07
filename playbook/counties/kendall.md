# Kendall County

Deliverables: plat map, zoning. **No legal description**: Kendall's recorded images are subscription only (Laredo). The assessor's abbreviated legal shown for the parcel goes to `fetch.py county --abbrev-legal`. No tax page. PIN: 10 digits `TT-SS-BBB-PPP`, shown hyphenated (`02-00-000-000`). Never buy documents or subscribe.

Domains: maps.co.kendall.il.us (the county GIS portal and its map viewers), kcgis-tax-maps.s3.us-east-2.amazonaws.com (where the tax map sheet PDFs download from), plus municipal zoning sites. Beware Kendall County, Texas (its maps show up in searches).

Map viewers paint through rAF: run the rAF patch (`recipes/browser.md`) after every navigation.

## Parcel lookup (the county test)

1. **Open** `https://maps.co.kendall.il.us/portal/home/index.html` and open the county's parcel viewer from it.
2. **Type** the address in the viewer's search box (house number and street, no suffix), pick the match, **click** the parcel and **read text** of its popup.
3. Several towns: pick the one whose city matches. The house number must be exactly the subject's.

Note: PIN, site address and city, municipality (UNINCORPORATED for county-zoned land), legal (the assessor's abbreviated legal, verbatim), lot dimensions when filled (the assessor's dimension string), zoning (filled for unincorporated parcels), acres, class. Point for zoning and the flood map: the middle of the lot, read from the viewer if it shows coordinates for a clicked point, otherwise from any public web map that does.

## Plat map (the county's scanned tax map sheet)

The county's GIS maps carry no printed dimensions. The tax map sheets are 300-dpi scans (11 x 17, 3300 x 5100 px) in PDF.

1. **Which sheet:** in the county portal's tax map viewer (or a viewer with the tax map sheet index layer), **click** the subject. The index gives each sheet's page, scale and year. Take the 1"=100' enlargement covering the subject (a page like `05-12A`) and its newest line sheet (type "line").
2. **Download it:** note the time (`python fetch/fetch.py now`) and **click** the sheet's own View or Download link (a real click). Chrome saves it to Downloads. The scan has no text: `python fetch/fetch.py grab-download --since <epoch> --name ".pdf" --dest "_data\_scratch\<page>.pdf"` and check it is the right page. It is working material: never put it in the property folder. If no file arrived, step 4 of `recipes/saving-files.md`.
3. **Render and crop** per `recipes/pdf-sheets.md`: `python fetch/tools/pdf.py render "_data\_scratch\<page>.pdf" "_data\_scratch\sheet" --dpi 300` (the full 3300 x 5100 scan), look at a reduced preview, find the subject by its lot number, the block-parcel label (`BBB-PPP`), the street names and the lot's shape in the viewer, then `python fetch/tools/stitch.py crop "_data\_scratch\sheet-1.png" "_data\_scratch\plat.png" X0 Y0 X1 Y1` around the subject lot, one parcel deep on every side and the nearest street name (no upscaling: the scan is the resolution). Look at the crop, check every bounding dimension is legible, then `fetch.py put --src "_data\_scratch\plat.png" --dest "<folder>\plat-map-<slug>.png"`.

Tested 2026-10 on a single-family lot: the sheet labels the subdivision with a short code (name plus unit number) and prints no block-parcel label for that lot, so the lot number, street name and the lot's shape found it; crop about 1700 x 700 px (six lots, the street, a municipal boundary line).

Checks (`deliverables/plat-map.md`): printed figures against the assessor's dimension string and acres from the viewer; a mismatch is a `fetch.py note` with both.

## Zoning

* **Unincorporated:** the parcel's zoning value is the county district; confirm in the county's zoning map (the county zoning layer, with ordinance number and year). Turn on its legend, search the subject, **click** it, **capture** map and legend. Say "unincorporated Kendall County zoning".
* **Yorkville** (tested): the city's own web map in the county portal, "Yorkville Property Information Map", colours each district and shows parcels with address labels: `https://maps.co.kendall.il.us/portal/apps/mapviewer/index.html?webmap=3f5e5e58c80340fbb2d4b8faedf326cb&center=<lon>,<lat>&level=18&marker=<lon>;<lat>;4326;<address>`, loaded inside a 900 x 900 frame (`recipes/municipal-zoning.md`). The Legend opens on the left; scroll it to the bottom for the Zoning key. The bare Yorkville zoning layer is one flat colour with no usable key: do not use it.
* **Minooka:** its zoning map in the county portal. **Oswego, Montgomery, Plano, Plainfield, Sandwich, Newark, Lisbon, Millbrook, Joliet** and others: `recipes/municipal-zoning.md`.

Capture and caption per `deliverables/zoning.md`.

## Run log facts

`Lot <n>, <subdivision>, <municipality or unincorporated> | sheet <page> (<year>); printed <dims>; county <ac> ac`. fetch.py adds the abbreviated legal and states that no recorded legal exists.
