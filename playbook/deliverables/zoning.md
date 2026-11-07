# Zoning: `zoning-<slug>.png`

Required for every address in every county. The county sheet says who zones the parcel and where its map is; `recipes/municipal-zoning.md` finds anything the sheet does not list.

## The standard (unchanged from the existing captures)

The image must show the subject parcel identified on the map together with the map key or legend, so the classification can be read off the exhibit itself. An identify panel or a record page that names the district confirms the code and gives the run log line, but it does not satisfy the deliverable on its own.

* **The subject must be identified in the frame**: the dropped search pin, the highlighted parcel, or the parcel's house number printed on the map. A picture of a coloured neighbourhood proves nothing.
* **The map's zoning key goes in every capture, no exceptions.** Whatever the source, find its zoning legend, capture it, and put it beside or above the map crop. Chicago's key is at the bottom of the Map Legend panel under "Zoning - Color-Coded"; a village PDF has a LEGEND block on the sheet. Without the key the reader cannot check the colour, so the exhibit is not self-proving.
* **The district must also be readable in words**: spelled out in an identify panel, printed on the parcel, or named by the legend row matching the subject's fill.
* **Caption the finished image** with the subject address, PIN, the district code and its plain-English name, and the source map with its date. Draw a ring around the subject on the map and say "circled" in the caption; keep the annotation obviously yours (white-haloed black ring, no map colour) so it can never be mistaken for map content. If the sheet is marked DRAFT or carries an adoption note, include the title block so that shows.
* **Address or PIN visible where the source offers it.** The Chicago identify panel prints both; a static map prints the house number in the lot. Include whichever is available.

**Hover** the mouse off the region before every **capture** you keep.

## Composing

`fetch/tools/zoning_compose.py` produces the usual layout: caption band on top, map on the left with the ring, key on the right.

```bash
python fetch/tools/zoning_compose.py --map "_data\_scratch\map.png" --legend "_data\_scratch\key.png" --ring <x> <y> --out "<folder>\zoning-<slug>.png" \
  --caption "<address> | PIN <pin> | Zoning: <code> <plain name>" \
            "Subject circled (<how it is identified>). <Municipality or Unincorporated County>." \
            "Source: <map name>, <viewer or adopted map PDF>. Captured <YYYY-MM-DD>."
```

`--ring x y` is the subject's position in map.png pixels. When the source is an identify panel plus map (Chicago), capture both in one region if they fit, otherwise as two captures composed the same way. Cut each piece with `python fetch/tools/stitch.py crop`. Open the result and check it.

## Checks

* The address or PIN in an identify panel is the subject's (the viewer will happily identify whatever was clicked last). Never read the district off a floating map label: it sits at a parcel's visual centre and can belong to the neighbour.
* The subject's fill colour matches the legend swatch for the district the identify panel or printed label names. If they disagree, say so; do not guess.
* `INC` (Lake, DeKalb) or a blank county zoning field means the county does not zone it: go to the municipality. Never report INC as a district.
* Unincorporated parcels: say "unincorporated <County> County zoning" in the caption and the run log.
* A PUD suffix, or a PUD overlay drawn over the subject: one line in the summary that bulk standards may come from the PUD ordinance.
* Confirm the district exists in that municipality's ordinance before glossing it (the viewer's ordinance link, or the ordinance text on the town's site).

A zoning PNG that cannot be produced is a failed required item: record it with what was tried, so the address comes back.

## Run log

`fetch.py finish --zoning "<code> (<plain name>, <municipality or county source>)"`.
