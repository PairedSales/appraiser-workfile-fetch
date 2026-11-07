# MLS listings: `mls-listing-<year>-<MLS#>-<slug>.pdf`, one per listing

Every address, every county: the MLS search always runs. Save **every** MLS listing for the subject, any status (NEW, ACTV, CTG, PEND, CLSD, CANC, EXP, TEMP, RNTD), however old. Two or fewer go in the property folder; more than two all go in `<folder>\MLS Listings\`. The only MLS files are the PDFs, and only when a listing exists. There is no search screenshot.

Domains: connectmls.mredllc.com (sign-in chooser) and connectmls2.mredllc.com (the app). Uses the user's own signed-in Chrome session: never type credentials; a username or password form is LOGIN_WALL.

## Sign-in check

Check the connectMLS sign-in once, at the start of the run, before any procedure (RULES.md, The loop, step 3):

1. **Open** `https://connectmls.mredllc.com/ssologin.jsp`.
2. A live session lands on `connectmls2.mredllc.com/mls/home/home.jsp` with the user's name in the page title: signed in.
3. If the sign-in chooser shows, **click** **MRED MEMBERS** (the left button). That is fine: it only picks the member sign-in path and types nothing. If it then lands on the home page as in 2, signed in.
4. A username or password form, at any point: signed out. Never type into it.

Then record it: `python fetch/fetch.py signin --slug S --site connectmls --status signed-in` (or `--status signed-out`). Signed out records mls-listing, market-graphs and market-conditions as LOGIN_WALL without visiting them; tell the user to sign in to connectMLS in Chrome and run the fetch again. Signed in: the steps below run later in the `mls` procedure, for every address.

## Steps

1. **Open** `https://connectmls.mredllc.com/ssologin.jsp` (or `https://connectmls.mredllc.com/`; if the sign-in chooser shows, **click** **MRED MEMBERS**, the left button). A live session lands on `connectmls2.mredllc.com/mls/home/home.jsp` with the user's name in the title.
2. **Search with the SmartBar, read its matches from the page's own data.** In the hidden window the suggestion dropdown never paints (the app captured the browser's animation timer at load, so the rAF patch is too late), but the matches are there. Focus the bar with **run script** (`document.getElementById('input-0').focus()`; a click does not focus it while the window is hidden), then **type** `<house number> <street name>` with no suffix (`100 W Main`, `100 Main`). **Do not press Enter.** Wait about 6 s, then read the matches from the main world with **run script** (if your browser tool runs scripts in an isolated world, this script-element pattern is how it reaches the page's Angular; see `playbook/browser/`):

```js
const s = document.createElement('script');
s.textContent = "try { var c = angular.element(document.querySelector('md-autocomplete')).controller('mdAutocomplete');" +
  " document.body.setAttribute('data-x', JSON.stringify((c.matches || []).map(function (x, i) { return x.type === 'listing' ? i + ': ' + x.display : null; }).filter(Boolean).slice(0, 40))); }" +
  " catch (e) { document.body.setAttribute('data-x', 'ERR ' + e); }";
document.head.appendChild(s); (document.body.getAttribute('data-x') || '').replace(/[?=&]/g, ' ')
```

   Each match reads `<index>: <MLS#> - <address>, <city> | <STATUS> | $<price>` (NEW, ACTV, CTG, PEND, CLSD, CANC, EXP, TEMP, RNTD). No listing rows after one retype means no listing.
3. A row is the subject only if house number, street and city all match (older listings often have no street suffix; for a condo the unit must match too). No matching row: `fetch.py record --item mls-listing --status na --reason "no listing found <date>" --note "MLS none"`.
4. Open each matching row in turn by its index (search again before each one), again in the main world with **run script**: `angular.element(document.querySelector('md-autocomplete')).controller('mdAutocomplete').select(<index>)` (same script-element pattern). Wait about 8 s: the Full - Agent (Classic) report opens as the page (`search.jsp`, an MLS number search). Read the List Date from the report page text: `<year>` in the file name is its four-digit year. Do steps 5 and 6 for each.
5. **Print it with connectMLS's own dialog.** In a narrow window the printer icon sits in the "More" menu; open the dialog with **run script**: `Array.from(document.querySelectorAll('button')).find(e => /Print or Save as PDF/.test(e.textContent)).click()`, wait 4 s and take a **screenshot**. The Print Listings dialog shows "All listings returned by this search (1)" and **Full - Agent (Classic)** ticked: confirm it is the only report ticked and the three Search Criteria/Statistics/Map boxes are empty. Note the time (`python fetch/fetch.py now`), then **click** **Save as PDF** with a real click (top of the dialog, beside Preview, Print and Cancel; about (550, 60) in a 782-wide window). It must be a real click: Chrome blocks script-started downloads. Prefer Save as PDF (tested, clean file); the dialog's Print button now also works (silent print to PDF, 2026-10-31) and is the fallback if Save as PDF does nothing. Wait about 10 s (nothing visibly changes), then **click** **Cancel**. Tested 2026-10 on a single-family CTG listing (2-page PDF, saved as "Report (3).pdf" in Downloads).
6. `python fetch/fetch.py grab-download --since <epoch> --match "<MLS#>,<house number>" --dest "<folder>\mls-listing-<year>-<MLS#>-<slug>.pdf"` (more than two listings: `--dest "<folder>\MLS Listings\mls-listing-<year>-<MLS#>-<slug>.pdf"`; `recipes/saving-files.md`). The report is usually 2 pages and its text shows the MLS # and address.
7. Read MLS #, status, list price, list and contract dates, acreage, dimensions and multiple-PIN remarks from the PDF text (`python fetch/tools/pdf.py text <file>`) for the summary. If acreage or dimensions disagree with the county, or "Mult PINs" / "Multiple Parcels" appears, add a `fetch.py note` naming the other PIN (for example: the sale includes a vacant side lot, PIN 09-00-000-000, on the same deed).

Do not use download-by-email or any other export, and change nothing in the MLS (no saved searches, favourites, emails).

## Recording

* All saved: one record, `--status ok --note "MLS: <n> listings (<MLS#> <STATUS> <list date>, ...)"`. If some saved and some did not, record `--status failed` with the MLS numbers still missing in `--reason`.
* Login form: `--status failed --reason LOGIN_WALL --needs "sign in to connectMLS in Chrome"`.
* A domain refused: DOMAIN_REFUSED with the domain.
* MLS problems never fail an address.
