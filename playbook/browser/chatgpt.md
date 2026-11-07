# Browser adapter: ChatGPT and Codex

Read this if you are ChatGPT or Codex. You drive the user's own Chrome, where they are signed in to connectMLS, through a **Browser Use** session with **full CDP access** (Chrome DevTools Protocol). The user turns it on in ChatGPT under Developer mode, "Enable full CDP access". The fetch needs it: CDP is what takes full-resolution screenshots and runs JavaScript in the page.

## Use CDP, every time

* Every **screenshot** and **capture** is a CDP `Page.captureScreenshot`. Every **run script** is a CDP `Runtime.evaluate`. Do not fall back to reading page text only, or to a browser of your own: a browser that is not the user's Chrome has none of their sign-ins.
* Before the first site of a run, check it works: one `Runtime.evaluate` of `document.title` and one `Page.captureScreenshot` in the working tab.
* If CDP is not available or either call is refused, stop before any site and tell the user: "In ChatGPT, turn on Developer mode > Enable full CDP access, connect Chrome with Browser Use, then run the fetch again." Record nothing: the run has not started.
* Full CDP can change Chrome itself. The playbook's Never list still applies: no `Browser.*` download or permission settings, no cookies or storage calls, no network interception, no `Fetch.*` or `Network.*` requests of your own. Use CDP only for the actions in the table.

## Action map

| Playbook action | CDP |
|---|---|
| **open** `<url>` | `Page.navigate`, then wait for `Page.loadEventFired` (or poll `document.readyState`) |
| **read text** | `Runtime.evaluate` `document.body.innerText` |
| **find** `<what>` | `Runtime.evaluate` with `querySelector` or a text search; read the element's `getBoundingClientRect()` for its position |
| **click** `<what>` | `Input.dispatchMouseEvent` `mousePressed` then `mouseReleased` at the element's centre (CSS px). This is real input, so Chrome lets it start a download; a scripted `.click()` is not |
| **type**, **press** | `Input.insertText` for text; `Input.dispatchKeyEvent` `keyDown`/`keyUp` for Enter, Tab, arrows |
| **hover** | `Input.dispatchMouseEvent` `mouseMoved` |
| **run script** | `Runtime.evaluate` with `awaitPromise: true` and `returnByValue: true`; the value of the last expression comes back |
| **screenshot** | `Page.captureScreenshot`, format png, a quick look |
| **capture** `<region>` | `Page.captureScreenshot` with format png and `clip: {x, y, width, height, scale: 1}` in CSS px. Decode the base64 `data` and write it to `_data\_scratch\<name>.png`; that file is the capture. Check its pixel size |
| **resize** | `Browser.getWindowForTarget`, then `Browser.setWindowBounds` with width and height |

## Quirks

* **Coordinates** for CDP input and clips are CSS pixels of the page, not screenshot pixels. No conversion is needed.
* **Chrome zoom.** Some sites keep a Chrome zoom (Cook's are at 90 %). A clip at `scale: 1` then comes back at the zoomed size: trust the decoded file's pixel size, as `recipes/browser.md` says.
* **Bigger than the window.** `Page.captureScreenshot` with `captureBeyondViewport: true` can capture a region larger than the window, which can replace a tiled capture. Check the result: some map viewers only draw what is on screen, so the part beyond the window comes out blank. Then tile as in `recipes/tiled-capture.md`.
* **Hidden window.** When the Chrome window is behind others, maps may not draw (`recipes/browser.md`, rAF patch). `Page.bringToFront` before the capture also helps.
* **Approvals.** ChatGPT may ask the user to approve actions. Ask once at the start for the whole run, so a run is not stopped at every capture.

Found another difference? Add it here and send it back as a pull request (`CONTRIBUTING.md`).
