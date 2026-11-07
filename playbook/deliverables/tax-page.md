# Tax page: `tax-page-<slug>.pdf`

Cook and McHenry only (config.json). The other counties are deliberately tax free: do not go looking for a tax page there. Will gets the assessor property card instead (`deliverables/property-card.md`).

## The deliverable

A searchable PDF of the county's tax or assessor page for the PIN, printed by Chrome (since 2026-10-31; before that it was a stitched PNG, and an existing `tax-page-<slug>.png` still counts as done). The county sheet gives the page and what to hide before printing.

## Printing the page (shared by the county sheets)

1. **Read text** first to get the figures (they feed the cross-checks and the run log line).
2. Note the time just before printing: `python fetch/fetch.py now`. Then tidy for print in one **run script**: the county sheet says what to hide. Then set `document.title = '<Kind> <PIN> <street address>'` (Chrome prints the title in the page header and names the file after it) and fire the print: `setTimeout(() => window.print(), 100)`.
3. Wait about 7 s, then `fetch.py grab-download --since <epoch> --match "<PIN with dashes>" --dest "<folder>\<kind>-<slug>.pdf" --trim-blank` (`--trim-blank` drops a trailing page that holds only Chrome's header and footer).
4. Check it: `python fetch/tools/pdf.py info "<folder>\<kind>-<slug>.pdf"` gives the page count and `python fetch/tools/pdf.py text "<folder>\<kind>-<slug>.pdf"` shows the PIN, address and the panels the spec lists. The file has real, searchable text.
5. If the print does not land (grab-download exit 3 twice), fall back to the PNG capture in the county sheet and say so in the record note.


## Cross-checks (the reason the page is read)

* Lot size on the tax page against frontage x depth from the plat: agreement confirms both readings; a mismatch usually means a dimension was read off the wrong parcel. Small differences are normal on irregular lots.
* The document list against the deed captured for the legal description. A deed missing from the list may mean a document for another PIN (or a list that only shows recent years: say which).
* The address and township against the address being fetched and the tax map title.
* Property class against zoning (Cook: 2-xx residential, 3-xx multi-family rental, 5-xx commercial or industrial). A mismatch is worth a sentence: often a legal non-conforming use.

## Never

Pay taxes, add to a cart, or click anything on these pages beyond reading. Tax figures are the county's, not an appraisal.

## Run log facts

`class <c>, AV <value> (<year> cert), est mkt $<value>, lot <sf> sf, bldg <sf> sf, <year> billed $<amount>`.
