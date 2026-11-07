# Legal description: `legal-description-<slug>.png`

Counties with free recorded images only: Cook, DuPage, Kane, DeKalb (config.json decides). The others get the assessor's abbreviated legal in the run log instead, labelled as such, never presented as a recorded legal and never built into one.

## The deliverable

A cropped image of the **recorded** legal description, from the county recorder's own document image:

* Use the most recent conveyance deed (warranty, quit claim, trustee's, special warranty, executor's, certificate of title; DuPage calls them DEED, QUIT CLAIM DEED, NR DEED). Only if there is no deed, the most recent mortgage's Exhibit A. Skip assignments, releases, modifications, subordinations: they only reference the property. A transfer-on-death instrument is worth a note but is not the vesting deed.
* Frame tightly around the legal description paragraph (LOT ... IN ... SUBDIVISION ... COUNTY, ILLINOIS) and take in the adjacent PIN ("Permanent Index Number") and property address lines when they sit next to it: they prove the document matches the subject.
* Legible at 100 %. Zoom the viewer a step if the text is small. The red or diagonal UNOFFICIAL COPY watermark is expected.
* **Hover** the mouse off the region before the **capture** (`recipes/browser.md`).

## Checks

* The PIN and address on the document, or in the recorder's index panel, are the subject's.
* The lot and subdivision agree with the recorder's index string and with the plat map's lot number. Recorded deeds carry scanner and typist errors (NORHT for NORTH): never correct them silently, mention them in a note.
* Multi-parcel deeds: the subject's parcel may be on an exhibit page. Capture the paragraph that covers the subject.

## Never

Buy anything, add to a cart, or order certified copies. Everything used here is free to view.

## Run log facts

`Lot <n> in <subdivision>, <section/township/range in short>, plat rec <date> as Doc <no> | <deed type> <doc no> rec <date>` (shorten as the existing log lines do).
