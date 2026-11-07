# Recipe: getting files into the property folder

All commands run from the folder root. `<folder>` is the plan's `folder` (`Workfiles\<slug>`).

## Files you made (captures, stitched images, composed exhibits)

A **capture** is already a file on disk; its result gives the path. Tiles and previews belong in `_data\_scratch\`. For each finished file, after looking at it:

```
python fetch/fetch.py put --src "<work file>" --dest "<folder>\<kind>-<slug>.<ext>"
```

Then `fetch.py record ... --status ok` (it checks the file arrived).

## Files Chrome downloads or prints (MLS PDF, record cards, printed pages)

Save them the way a person would: Chrome puts them in the user's Downloads folder. That folder is linked to the project, and `local.json` (`downloads_dir`) tells fetch.py where it is.

1. Just before clicking, note the time: `python fetch/fetch.py now`.
2. **Click** the site's own Download, View PDF, Save as PDF or Print control (a real click). With the Chrome setup on, a PDF link downloads and a Print button (or `window.print()`) saves a PDF of the page silently, named after the page title. Wait about 8 s.
3. Copy it into the property folder:

```
python fetch/fetch.py grab-download --since <epoch> --match "<house number>,<distinctive street word>" --dest "<folder>\<kind>-<slug>.pdf"
```

   It takes the newest file made since then whose text contains every match word and copies it into place (temp name, then rename). Chrome appends " (1)", " (2)" to repeated names, so files are identified by content, never by name. For an MLS PDF, match on the MLS number too. A scanned PDF has no text: use `--name ".pdf"` (the newest PDF since the click) and check its pages. A printed page sometimes lands in the last folder anyone picked in a Save as PDF window instead of Downloads; grab-download also looks for new PDFs elsewhere in this folder (never in `Workfiles` or `_data`) and moves such a stray to `_data\_to_delete` (`stray_moved_to` in its output).
4. Exit code 3 means nothing matched. Wait about 10 s and run it once more. Still nothing: record the item failed with the reason fetch.py printed, the control you clicked and what you saw. `DOWNLOAD_NOT_REACHABLE` means the Downloads folder is not where `local.json` says: `--needs "run python fetch/fetch.py doctor and link the Downloads folder to the project"`. A print that saved nowhere fetch.py can see: `--reason PRINT_FAILED --needs "in Chrome, Ctrl+P > Save as PDF once into Downloads"`. Exit code 4 is TOOL_MISSING: run `fetch.py doctor`, fix what it lists, then try once more.

Do not work around a download that did not land: never screenshot or render the PDF to PNG in its place, never script a download, never change Chrome settings and never point Chrome at another download folder.

A document that is only a web page with no download control: where the deliverable spec asks for a PDF, use the site's own Print button (or `window.print()`); otherwise follow the spec (most such pages are PNG captures). If the spec has no PDF form for it, record `ON_SITE_ONLY`.
