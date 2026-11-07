# Recipe: capturing a map or page bigger than one screen

**Prefer fewer tiles.** One legible capture beats a big stitch: zoom the map until the labels you need read, frame the subject, and try a single capture first. Tile only when one capture cannot hold everything the spec needs at a legible size.

## Show only what you capture

Browser tools time out or downscale a large capture (your tool's file in `playbook\browser\` gives the limit; about 900 x 900 CSS px is safe). So:

* Before capturing, **run script** to hide what is not part of the image: side panels, headers, toolbars, banners, chat widgets (`style.visibility = 'hidden'`, or `display = 'none'` where the map should take the space). Never hide the map's own scale bar, north arrow or legend when the spec needs them.
* **Capture** only the region you keep, at most one tile. The result's pixel size must equal the region's size (Chrome zoom differs per site; trust the reported size, `recipes/browser.md`).
* **Hover** in a far corner before every capture you keep.

## Tiles, panned with the page's own controls

1. Frame the top-left tile: the map at the zoom you want, the subject inside the area you will cover. Pick the tile size `T` (in your tool's coordinates) and a capture region `[x, y, x + T, y + T]` inside the map, clear of its zoom buttons and overlays.
2. **Capture** the tile. Record its path with its (col, row).
3. Pan by exactly one tile with the page's own controls: drag the map from a point inside it by `T` (left by `T` for the next column; up by `T` for the next row; back to column 0 by dragging right). Drag slowly so the map does not glide on after the release. Arrow keys or pan buttons also work once you have measured their step (pan once, see how far a landmark moved).
4. Check the shift before the next capture: a landmark (a street corner, a label) should have moved exactly `T`. If it moved a different amount, pan by the difference. Wait for the map to finish drawing (no blank squares) and **capture** again.
5. Repeat for each tile. Keep the zoom unchanged: never use the mouse wheel between tiles.

If a capture times out, too much is painted: hide more of the page and retry once. A tab that keeps timing out is wedged: open a new tab (do not close the old one mid-run) and start the tiles again there.

## Stitch

```
python fetch/tools/stitch.py grid --tile TW TH --out "_data\_scratch\<kind>.png" 0,0=a.png 1,0=b.png 0,1=c.png 1,1=d.png
python fetch/tools/stitch.py preview "_data\_scratch\<kind>.png" "_data\_scratch\preview.png"
```

`TW TH` is the captured tile size in pixels (from the capture results). `grid` resizes every tile to exactly that and pastes it at (col x TW, row x TH); `--crop W H` trims the result. Open the preview and check every seam: lines and labels continue across it with no step or gap. A seam that is off means a pan was off: recapture that tile.

To trim a capture or the stitched image: `python fetch/tools/stitch.py crop IN.png OUT.png X0 Y0 X1 Y1` (pixels of IN.png).

Other shapes:

* A long web page: `recipes/html-capture.md` (`stitch.py page`), or scroll by a set amount between captures and `stitch.py vstack --out OUT.png t1.png t2.png`.
* A PDF sheet: no tiles at all, render it on disk (`recipes/pdf-sheets.md`).
