# Recipe: a PDF the site serves (deed, tax map sheet, zoning map, FIRMette)

The site hands over the PDF with its own View, Download or Print control. Save it, render it on disk, crop it. Never open a PDF in a tab: with the Chrome setup on (`setup\chrome\`), a PDF link downloads to Downloads instead. A PDF that opens in a tab means the setup is off: record the item failed with `--needs "run setup\\chrome\\chrome-automation-on.reg"`.

## 1. Download it

1. **Find** the document on the site's own page (the recorder's document row, the tax map page link, the town's zoning page, FEMA's FIRMette result).
2. Note the time: `python fetch/fetch.py now`.
3. **Click** the site's own View, Download or Print control (a real click). Wait about 8 s.
4. Copy it out of Downloads:

```
python fetch/fetch.py grab-download --since <epoch> --match "<words in its text>" --dest "_data\_scratch\<name>.pdf"
```

   Match on words the document prints (the PIN, the house number and a street word, the sheet's township name, "FIRMette"). A scan has no text: use `--name ".pdf"` (the newest PDF since the click) and check its pages. Exit codes and what to record are in `recipes/saving-files.md`. When the PDF itself is the deliverable (MLS listing, township record card, tax page), `--dest` is the property folder file and you are done.

## 2. Render it

```
python fetch/tools/pdf.py info "_data\_scratch\<name>.pdf"
python fetch/tools/pdf.py text "_data\_scratch\<name>.pdf"
python fetch/tools/pdf.py render "_data\_scratch\<name>.pdf" "_data\_scratch\<prefix>" --dpi 300 [--pages N] [--clip X0 Y0 X1 Y1]
```

`info` gives the page count and page sizes in points; `text` shows which page holds the subject (deeds: the legal description page; multi-page atlases: the sheet naming the subject's block or section). `render` writes `<prefix>-<N>.png`, one per page. Pixel = point x dpi / 72.

* **dpi**: 300 for deeds and letter or tabloid sheets. A big sheet (a 36 x 48 in zoning map is 10800 x 14400 px at 300) renders at 150 to 200; go higher only if the labels you need do not read.
* To find the subject on a big sheet, render once small (`--dpi 50`) and look at it. Then render only that region with `--clip X0 Y0 X1 Y1` (PDF points from the top left: pixel at dpi 50 x 72 / 50). A clip renders a small area of a big sheet at a high dpi (600 to 2000) without rendering the whole page.

## 3. Crop and save

**Look at** the render, then cut the region the deliverable spec asks for:

```
python fetch/tools/stitch.py crop "_data\_scratch\<prefix>-<N>.png" "_data\_scratch\<kind>.png" X0 Y0 X1 Y1
python fetch/tools/stitch.py preview "_data\_scratch\<kind>.png" "_data\_scratch\preview.png"
```

Coordinates are pixels of the render. Open the crop and check it against the spec (every needed label legible, nothing cut off at an edge), then `python fetch/fetch.py put --src "_data\_scratch\<kind>.png" --dest "<folder>\<kind>-<slug>.png"`. A legend or title block on the same sheet is a second crop.

A PNG cut from the PDF is the deliverable only where the spec asks for a PNG (plat map, legal description, zoning, flood map). Where it asks for the PDF, save the PDF.
