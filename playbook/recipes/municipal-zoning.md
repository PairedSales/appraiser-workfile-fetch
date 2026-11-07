# Recipe: finding and capturing a municipality's zoning

Each municipality zones itself; the county zones only unincorporated land. The county sheet says how to tell which applies and lists the municipal maps already proven. The capture standard is in `deliverables/zoning.md`.

## Find the town's zoning map

1. **County sheet first.** It lists municipal viewers and PDFs already proven in that county.
2. **Web search** `<town> IL zoning map`. Take only the municipality's own site, or a viewer or document its site links to (many towns publish through a GIS vendor or a consortium viewer, for example `communitymapviewer.gisconsortium.org/<Town>IL`). Beware look-alikes in other states (there is a Kane County in Utah, a Kendall County in Texas, a DeKalb County in Georgia), consultants' drafts and third-party zoning aggregators.
3. You want one of two things:
   * an **interactive zoning viewer** with an address search and a legend, or
   * the **adopted zoning map PDF** (planning or community development page; "Official Zoning Map", with an adoption date).

   Prefer the viewer when it shows the subject's district in words; use the PDF when there is no viewer, the viewer sits behind a terms box, or it will not draw.

## Interactive viewer

1. **Open** it. Do not tick terms or disclaimer boxes: a viewer gated that way is not used.
2. **Type** the address in the viewer's own search box and pick the matching result. Check the pin or highlight lands on the subject (house number on the map, lot shape against the county viewer).
3. **Click** the parcel. Read the identify panel: the zoning district, and the address or PIN it identifies. Confirm they are the subject's.
4. Turn on the zoning layer if it is not already on, open the viewer's **Legend** and scroll it to the zoning key.
5. **Capture** the map with the subject in it, and the legend with the zoning key, together if they fit, otherwise as two captures. Close any popup that covers the subject first, hide side panels and banners (`recipes/tiled-capture.md`, Show only what you capture). If the capture times out because the viewer paints too much, hide more of the page or **resize** the window (RULES.md) and retry once.
6. Crop each capture to the map and to the zoning section of the key (`python fetch/tools/stitch.py crop`) and compose with `fetch/tools/zoning_compose.py` (`deliverables/zoning.md`), the ring on the subject.

A viewer whose legend shows no zoning key (every district one colour, "No legend"): use the identify panel for the district in words and take the key from the adopted PDF's LEGEND block, if it matches the viewer's colours; otherwise use the PDF for the whole exhibit.

## Adopted zoning map PDF

1. **Click** the PDF link on the town's own page and save it (`recipes/pdf-sheets.md`).
2. Render it small, find the subject: street names are printed; follow them to the subject's block and match the lot by shape and position against the county parcel viewer (house numbers are printed on some sheets).
3. Render at full dpi and crop the subject with enough streets around it to be self-locating; crop the LEGEND block separately; crop the title block if it is marked DRAFT or carries an adoption note.
4. Compose as above. Say the district was read from the adopted map by colour (and printed label, if there is one).

## Unincorporated

The county's own zoning viewer, the same way as an interactive viewer (the county sheet names it).

## Nothing usable

If nothing can be driven reliably, record zoning as failed (OTHER, saying what was tried) and name the municipality's planning department in `--needs`. Never use a third-party zoning aggregator, never guess a district, never infer it from the neighbours.
