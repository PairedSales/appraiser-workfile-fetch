# Flood map: `flood-map-<slug>.png`

Every address. FEMA's own FIRMette with the subject pinned, plus the flood facts for the run log. Free, no sign-up. Domain: msc.fema.gov (FEMA's Map Service Center).

## 1. Search the address

1. **Open** `https://msc.fema.gov/portal/search`.
2. **Type** the full address (number, street, town, IL, ZIP) in the page's search box and search. Pick the suggestion that matches the house number, street and town; a street-only or town-only match is uncertain (see Recording).
3. **Read text** of the results: the effective FIRM panel for the location and its effective date, the community, and any Letters of Map Change (LOMR, LOMA) listed for that panel. Check the map's pin sits on the subject's street and block.

## 2. Make the FIRMette

Use the results page's own FIRMette control (a "Dynamic FIRMette" or "Print FIRMette" link or button; it may ask you to **click** the location on the map: click the subject's pin). FEMA builds a PDF and offers it for download. Save it per `recipes/pdf-sheets.md`:

```
python fetch/fetch.py now
(click the site's control that downloads the FIRMette PDF)
python fetch/fetch.py grab-download --since <epoch> --match "FIRMette" --dest "_data\_scratch\flood-<slug>.pdf"
python fetch/tools/pdf.py render "_data\_scratch\flood-<slug>.pdf" "_data\_scratch\flood-<slug>" --dpi 150 --pages 1
```

If `--match "FIRMette"` finds nothing, try `--name ".pdf"` once and check it is a FIRMette. A job that fails or never offers a download: one retry, then record PRINT_FAILED.

## 3. Read it

Open `_data\_scratch\flood-<slug>-1.png` and `python fetch/tools/pdf.py text` of the PDF. Read:

* **Zone** under the pin, from the FIRMette's shading and zone labels against its own legend. `SFHA` is yes for A, AE, AH, AO, AR, A99, V and VE. Tell minimal-hazard X (unshaded) from 0.2 % X (shaded). The pin on a zone line: report both zones.
* **BFE**, inside an SFHA where the map prints one (an elevation label or a BFE line near the pin).
* **Panel and effective date** from the FIRMette's title block; it must include the panel the results page named. Other panels' labels can show near a panel edge.
* **Nearest SFHA**, outside an SFHA: measure on the image from the pin to the nearest SFHA shading, in pixels, and convert with the scale bar (measure the bar's labelled length in pixels). It is an estimate: round to a range ("200-300 ft"). No SFHA anywhere on the FIRMette: "over <distance from the pin to the nearest map edge> ft".
* The "exported on" stamp, the pin, the legend, the panel number and date must all be readable at this render. If small text does not read, render again at `--dpi 200`.

The zone and panel on the FIRMette must agree with the results page. If they do not, say so in a note; do not pick one.

## 4. Save

`python fetch/fetch.py put --src "_data\_scratch\flood-<slug>-1.png" --dest "<folder>\flood-map-<slug>.png"` (`recipes/saving-files.md`).

## Recording

* `--status ok --note "Flood: zone <zone>, SFHA <yes|no>, panel <FIRM panel> eff <YYYY-MM-DD>[, BFE <value>][, nearest SFHA <range> ft (est.)][, LOMR/LOMA yes]"`.
* Inside an SFHA: also `fetch.py note --text "INSIDE SPECIAL FLOOD HAZARD AREA: zone <zone>"`, and say so prominently in the report.
* Point on a FIRM panel boundary (the pin on a panel line, or the results page names two panels): not a failure. Save the file, record the item ok as above, then `python fetch/fetch.py note --slug S --text "Flood point is on the boundary of panels <a> and <b>; check which panel applies"`.
* SFHA or shaded X shading within about 100 ft of the pin, or reaching any part of the lot as the county viewer draws it: a note recommending a flood determination, saying which zones the lot touches.
* The search matched only the street or the town: record ok only if the pin is clearly on the subject's lot; otherwise `--status failed --reason UNCERTAIN_MATCH --seen "<what the search returned>"`.
* FEMA down, domain refused, print failed: record it failed with the reason; it never fails the address.
