# Plat map: `plat-map-<slug>.png`

Every county. The county sheet names the source: the county's tax map PDF sheet, or the county's own parcel viewer.

## The deliverable

A tight, sharp crop of the **subject lot**, not a picture of the block. Resolution beats coverage every time.

* The whole subject lot, one parcel deep on every side (or out to the street or block line, whichever comes first), and the nearest street name so the crop is self-locating.
* Every dimension bounding the subject legible: frontage, both sides, rear. Figures are often printed inside a neighbouring parcel, and a run of equal lots may only be dimensioned at its ends; widen the crop just enough to take them in.
* No caption and no annotation: the sheet's own lot and parcel numbers identify the subject. (A viewer's own highlight of the subject is fine.)

## Getting it

* **Tax map PDF sheet**: save the sheet from the county's own page and render it on disk (`recipes/pdf-sheets.md`). Long edge of the crop about 2000 to 3000 px. Blurry text means something other than the on-disk render was cropped.
* **County parcel viewer**: search the address or PIN in the viewer's own search box, turn on the dimension or lot-line labels the county sheet names, and zoom with the viewer's own controls until every bounding dimension reads. Hide panels and capture the map (`recipes/tiled-capture.md`): one capture when the lot fits legibly, tiles panned with the viewer's controls when it does not.

## Identify the subject before cropping

Cross-check the parcel number printed in the lot against the PIN, and the lot number against the legal description or the assessor index. That is the single best guard against cropping the neighbour.

## Checks after capture

Against what the record shows, not against computed shapes:

* **Every bounding dimension is visible.** A missing side means widen and capture again. Never ship a crop with a bounding dimension cut off.
* **Area**: frontage x depth from the printed figures (or the sum of the parts on an irregular lot) against the assessor's or tax page's lot size and the deed's lot. Small differences are normal on irregular lots.
* **Lot and subdivision** on the map against the legal description or the assessor index.

A mismatch is a `fetch.py note` with both figures and which you trust (the recorded plat is the tiebreaker), never averaged. Condos: the plat is the common parcel footprint, not the unit; note it.

## Run log facts

`tax map <page> (<year>); <frontage> x <depth> (or the printed figures side by side) = <sq ft> vs <county figure> sf` (or `county viewer` in place of the tax map page) and anything that did not reconcile.
