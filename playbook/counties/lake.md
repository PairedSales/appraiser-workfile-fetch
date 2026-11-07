# Lake County

Deliverables: plat map, zoning. **No legal description**: Lake County publishes no free recorded document images. Do not look for one, do not sign up for anything, never substitute or build one from the assessor's index; the assessor's abbreviated legal goes to `fetch.py county --abbrev-legal`, labelled as such in the run log. No tax page (ignore the assessed values and sale amounts the viewer shows). PIN: 10 digits `TT-SS-BBB-PPP` (for example `11-00-000-000`); the viewer may show it unhyphenated, the tax map prints all 10.

Domains: maps.lakecountyil.gov (the county's Tax Parcel Viewer), tax.lakecountyil.gov (property tax information, a second place to read the PIN, township and legal), communitymapviewer.gisconsortium.org and www.arcgis.com (municipal zoning). Never buy documents.

Read `recipes/browser.md` first: the viewer paints through rAF, so run the rAF patch after every navigation.

## Parcel lookup (the county test: two gates, both must pass)

1. **Open** `https://maps.lakecountyil.gov/taxmapgallery` (the retired gallery; it links to the new Tax Parcel Viewer) and **click** through to the viewer. Run the rAF patch.
2. **Type** the address in the viewer's search box and **press** Enter, or pick the matching suggestion.
3. **Click** the parcel under the result and **read text** of its popup or details panel.

Gate 1: the search finds the address at all. No match means it is probably not in Lake County. A suggestion on a same-named street in another Lake County town is **not** a match (out-of-county addresses have matched same-named streets here).
Gate 2: the parcel you clicked shows the given house number and street as its site address. A search pin in the road between lots: click the lots on each side and take the one whose address matches. Nothing matching means gate 2 failed. A weak city match alone is fine (unincorporated addresses carry the nearest post office town). Never capture a neighbouring lot.

Note from the parcel details: PIN, site address, municipality (UNINCORPORATED means the County zones it), township, zoning, the tax map page (for example `LIBE111`), lot area, class, and the legal description lines. Abbreviated legal: the legal lines joined in order, verbatim. If the viewer does not show the legal, **open** tax.lakecountyil.gov, search the PIN, and **read text** of the parcel page.

Point for zoning and the flood map: the middle of the subject lot, not the search pin. Read the coordinates from the viewer if it shows them for a clicked point; otherwise the lot's centre from any public web map that shows coordinates for a clicked point.

## Plat map (the viewer's own map)

1. In the viewer, with the subject selected, open the layer list and make sure the parcel lines, the dimension labels, road names and address labels are on. Leave any old or superseded dimension layer off, or old figures print over the current ones.
2. Zoom in with the page's own controls until the lot dimensions draw: they only appear at large scale (closer than about 1:1250; parcel lines drop out beyond about 1:1550). Centre the subject.
3. Hide the side panels, search box and other clutter (**run script**), **hover** off the map, **capture** the subject lot, one parcel deep on every side and the nearest street name. If that will not fit legibly in one capture, `recipes/tiled-capture.md`.
4. Look at it: every dimension bounding the subject readable, the subject's parcel number in the lot. `fetch.py put` per `recipes/saving-files.md`.

Historic tax map pages: layer list, turn on **Survey and Historic Tax Map Images**, then click the map. Only for checking an old call; the current viewer is the deliverable.

Checks (`deliverables/plat-map.md`): the Lake parcel polygon is **not** the platted call. Expect the drawn lot to run a foot or several long; the assessor's lot area usually matches the polygon rather than the printed calls. Compare printed frontage x depth with the lot area the viewer shows and report both when they diverge; the recorded plat would be the tiebreaker and this county does not provide it.

## Zoning

* **Unincorporated:** the parcel's own zoning value is the county UDO district (`R-1`, `E`, `AG`). In the viewer, turn on the County UDO zoning layer (and the PUD layer if there is one; a PUD hit is worth a line), turn on its legend, zoom to the subject and capture map and legend. Say "Lake County UDO zoning (unincorporated)".
* **Incorporated:** a zoning value of `INC` means the county does not zone it: **never report INC**. Most municipalities are GIS Consortium members: **open** the town's Community Map Viewer on communitymapviewer.gisconsortium.org (the town's viewer is named like `LibertyvilleIL`, `MundeleinIL`), search the address, turn on its Zoning layer and legend, click the parcel to read the district and its description, capture. Proven in Libertyville (R-5), Mundelein (C5-MU) and Lake Zurich (R-5). A consortium page may sit in a frame: **open** the frame's own address so it is the top-level page (`recipes/browser.md`).
* **Not a member:** the town's own zoning map or viewer via `recipes/municipal-zoning.md`. Beware other states' Lake Counties.

Capture and caption per `deliverables/zoning.md`.

## Run log facts

`<subdivision and lot>, <township> Twp, map page <page> | printed <dims>; areas <printed frontage x depth> vs <viewer lot area> sf` and anything unreconciled. fetch.py adds the abbreviated legal and states that no recorded legal exists.
