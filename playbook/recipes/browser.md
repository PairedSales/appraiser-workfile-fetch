# Recipe: browser facts that shape every capture

Read before the first capture of a run. These hit every county. Your browser tool's own quirks are in `playbook\browser\`.

## The window is often hidden

When the AI drives Chrome, `document.visibilityState === 'hidden'` much of the time. Then:

* `requestAnimationFrame` never fires. Anything that paints through it (county map viewers, the connectMLS suggestion dropdown, Infosparks) hangs or stays half drawn with no error.
* If three different actions give an identical screenshot, the renderer is frozen: switch approach instead of retrying.

**rAF patch.** Patch the page's own JavaScript (its main world) by injecting a script element. **Run script** after every navigation (it is lost on navigate), then wait about 5 s:

```js
const s = document.createElement('script');
s.textContent = "window.requestAnimationFrame=function(cb){return setTimeout(function(){cb(performance.now())},16)};" +
                "window.cancelAnimationFrame=function(id){clearTimeout(id)};";
document.head.appendChild(s); 'patched'
```

## PDFs

With the Chrome setup on (`setup\chrome\chrome-automation-on.reg`), Chrome's built-in PDF viewer is off: a PDF link or a site's View PDF button downloads the file to Downloads instead of opening a tab. Never try to read a PDF in a tab; save it and read it from disk (`python fetch/tools/pdf.py text <file>`; map sheets and deeds are rendered with `recipes/pdf-sheets.md`). If a PDF opens in a tab, the setup is off: record the item failed with `--needs "run setup\\chrome\\chrome-automation-on.reg"`.

## Scripts

* Cross-origin iframes take no synthetic input. **Open** the iframe's own `src` so it becomes the top-level document.
* Do not trigger alerts or confirms. With the Chrome setup on, any Print button, Ctrl+P or `window.print()` saves a PDF with no dialog and the tab stays responsive (`recipes/saving-files.md`).

## Captures

* **Show only what you capture.** Many browser tools time out or downscale on a large capture (the adapter gives the limit; 900 x 900 CSS px for Claude in Chrome). So never capture a whole window: show only the thing being captured, at most one tile (hide side panels, banners and toolbars; a band of an HTML page, `recipes/html-capture.md`; a bigger map in screen-sized pieces, `recipes/tiled-capture.md`).
* **Chrome zoom differs per site** (Cook's sites sit at 90 %) and `innerWidth` / `devicePixelRatio` can read differently from one call to the next. Trust the pixel size the **capture** result reports: a tile meant to be 900 x 900 must come back 900 x 900.
* **Hover off the region** (a far corner) before every capture you keep, or the cursor lands on the text.
