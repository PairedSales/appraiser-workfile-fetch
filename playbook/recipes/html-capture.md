# Recipe: capturing a web page (an HTML record, not a map)

For record pages that are plain HTML (township assessor cards, the Will SOA card). A record that fits in one tile (about 900 x 900 CSS px, `recipes/tiled-capture.md`) is one capture of its box. A bigger one is shown one tile at a time with a `clip-path` on the page root, captured 1:1 and stitched. Everything here only changes how the open page looks. Tested 2026-10-25 on a township assessor card (2 x 2 tiles in a 2347-px window).

1. **Tidy the page.** **Run script** `window.scrollTo(0, 0)`, then hide buttons, the print icon, "Back" links, search boxes and any "comparable properties / nearby sales" block (`style.visibility = 'hidden'`, or `display = 'none'` for a block below the record so the page gets shorter). Never click anything to do it.
2. **Measure the record**: the union of its tables and images, plus 8 px. **Run script**:

```js
window.scrollTo(0, 0);
const root = document.querySelector('<the record container>');          // e.g. the DNN module, main, #content
const rs = Array.from(root.querySelectorAll('table, img, h2, h3, dl')).map(e => e.getBoundingClientRect())
  .filter(r => r.width > 0 && r.height > 0);
const b = [Math.min(...rs.map(r => r.x)) - 8, Math.min(...rs.map(r => r.y)) - 8,
           Math.max(...rs.map(r => r.right)) + 8, Math.max(...rs.map(r => r.bottom)) + 8].map(Math.round);
JSON.stringify({b, iw: innerWidth, ih: innerHeight})
```

   The window must be taller than the record (`ih` > `b[3]`) so nothing scrolls; if not, **resize** it (read and restore `outerWidth`/`outerHeight`, RULES.md).
3. **One tile at a time.** cols = ceil((b2 - b0) / 900), rows = ceil((b3 - b1) / 900); tile (col, row) starts at x0 = b0 + 900 col, y0 = b1 + 900 row. The insets are against the root's own box, or the bottom of a tile comes out blank. **Run script**:

```js
const H = document.documentElement, r = H.getBoundingClientRect(), x0 = <x0>, y0 = <y0>;
H.style.clipPath = `inset(${y0}px ${Math.max(0, r.width - x0 - 900)}px ${Math.max(0, r.height - y0 - 900)}px ${x0}px)`; 'ok'
```

4. **Capture.** **Hover** to a far corner, take a small **screenshot** (it wakes the renderer and gives the frame size), then **capture** the tile's CSS box times `k` (`k` = screenshot frame width / `innerWidth`). A full tile comes back about 900 x 900 (901 is normal); edge tiles are smaller. Clear the clip afterwards (`H.style.clipPath = ''`), even when a step fails.
5. **Stitch**: `python fetch/tools/stitch.py page --tile 900 --out "<folder>\<kind>-<slug>.png" 0,0=t00.png 1,0=t10.png 0,1=t01.png ...` (each tile pasted as captured, trimmed to the non-white area plus 10 px). Look at it: every row of every table present, no seam through a line of text.
