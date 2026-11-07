# Property card: `property-card-<slug>.pdf`

Will County only (config.json). The Supervisor of Assessments property record card (PRC) at willcountysoa.com, free, no sign-in. It is the best single source in Will County: township, subdivision, property class, assessments, sales with document numbers, building data and the assessor's legal description. The county sheet (`counties/will.md`) has the exact steps.

## The deliverable

A searchable PDF of the whole card, from the county header down to the Legal Description, printed by Chrome (since 2026-10-31; before that it was a stitched PNG, and an existing `property-card-<slug>.png` still counts as done). Printed per `deliverables/tax-page.md`, "Printing the page", with the page buttons hidden (Prev Parcel, Next Parcel, View Tax Map, Property Search Portal). Every row of the Assessment table and the Legal Description must be in the PDF text.

## Cross-checks

* PIN on the card against the PIN from the parcel lookup.
* Street address and city against the address being fetched. The card can show only a street with `(PVT)` and no house number on new construction; that is not a mismatch when the PIN matches.
* Subdivision and lot in the Legal Description against the lot number on the plat map.
* Sale Information: a sale in the last 12 months goes to `fetch.py note` with its date, amount and document number.
* "There is no building information currently available" means new construction or a vacant lot: say so in the note (the township assessor has not picked up the building yet; the class is usually 0032 / 0030 with land only).

## Never

Click anything on the card beyond reading. Never follow the Treasurer link to pay anything.

## Run log facts

`card: class <c>, <township>, AV <total> (<year> <level>), mkt $<value>, sale <date> $<amount> <doc>, bldg <style>/<year built>/<sq ft> sf` (or `no building data`).
