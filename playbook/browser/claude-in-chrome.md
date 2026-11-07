# Browser adapter: Claude in Chrome

Read this if your browser tools are the Claude in Chrome extension (tool names start `mcp__claude-in-chrome__`). It is the only file in the playbook that names these tools. Everything else says **open**, **click**, **capture** and so on (RULES.md, Browser actions).

## Load the tools

If the tools are deferred, load them in one ToolSearch call:

```
select:mcp__claude-in-chrome__tabs_context_mcp,mcp__claude-in-chrome__navigate,mcp__claude-in-chrome__computer,mcp__claude-in-chrome__get_page_text,mcp__claude-in-chrome__find,mcp__claude-in-chrome__browser_batch,mcp__claude-in-chrome__tabs_create_mcp,mcp__claude-in-chrome__tabs_close_mcp,mcp__claude-in-chrome__javascript_tool,mcp__claude-in-chrome__resize_window
```

Call `tabs_context_mcp` first and work in the tab group it gives you. Close the tabs you opened only at the very end of the run: closing a tab mid-run can drop the whole tab group, after which every call fails with "not in Claude's tab group" (if that happens, call `tabs_context_mcp` with `createIfEmpty` and carry on in the new tab).

## Action map

| Playbook action | Tool call |
|---|---|
| **open** `<url>` | `navigate` with the URL |
| **read text** | `get_page_text` |
| **find** `<what>` | `find` with a plain description |
| **click** `<what>` | `computer` `left_click` at the element's coordinates (screenshot pixels) or its `ref` from `find` |
| **type**, **press** | `computer` `type` / `key` |
| **hover** | `computer` `hover` |
| **run script** | `javascript_tool` |
| **screenshot** | `computer` `screenshot` (pass `scale: 0.2` for the small wake-up shot) |
| **capture** `<region>` | `computer` `zoom` with `region: [x0, y0, x1, y1]` and `save_to_disk: true`, **no `scale`**. The result gives the saved path and the pixel size |
| **resize** | `resize_window` |

Several steps that do not depend on each other's output can go in one `browser_batch`. Retry a capture that times out once as a standalone call, not inside `browser_batch`.

## Quirks of this tool

* **Isolated world.** `javascript_tool` runs in an isolated world: it sees the DOM but not the page's own JavaScript globals. To reach the page's globals (rAF patch, Angular), inject a `<script>` element (`recipes/browser.md`).
* **Top-level `await`** works and the last expression is returned. On some pages `window.__x` values set by one call vanish before the next: do the whole step in one call.
* **Filtered output.** Output containing `?`, `=` or `&` comes back as `[BLOCKED: Cookie/query string data]`. End with `.replace(/[?=&]/g,' ')`, or to read a URL back intact replace `?` with `[Q]`, `=` with `[EQ]`, `&` with `[AMP]` and rebuild it yourself. Base64 payloads are filtered too: never read a canvas or file back through `javascript_tool`; **capture** is the supported path.
* **Alerts and confirms freeze the extension.** Never trigger one. Printing does not freeze it once the Chrome setup (`setup\chrome\`) is on.
* **Capture size limit.** A `zoom` capture times out ("renderer may be frozen") when much more than about 900 x 900 CSS px of the page is painted, especially when the display is asleep. That is why the playbook tiles at 900 x 900. Even a `scale: 0.3` screenshot of a full page can time out; that is the same limit, not a dead browser.
* **Wake the renderer.** The first `zoom` after a script call or a pause often fails with "renderer may be frozen". Take a `screenshot` with `scale: 0.2` first, then the `zoom`.
* **Never pass `scale` on a `save_to_disk` capture**: the saved file would be the downscaled one.
* **Coordinates** passed to `computer` are screenshot pixels. Measure once per tab: `k = screenshot_width / window.innerWidth`. A `zoom` capture comes back at roughly CSS-pixel resolution (1:1), which is what makes tiling work.
* **Domain permission.** "Permission denied for this action on this domain" means the extension has not been allowed on that site. Retry once after about 10 s, then record DOMAIN_REFUSED (`--needs "allow <domain> in the Claude in Chrome extension"`).
* **File URLs.** For downloads to be found, turn on "Allow access to file URLs" for the extension (chrome://extensions, Details).
* **Extension unreachable:** record BROWSER_UNAVAILABLE and stop the run (RULES.md, Browser actions).
