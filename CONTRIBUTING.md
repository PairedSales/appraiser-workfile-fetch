# Contributing

County and township sites change their pages a few times a year. When one does, a step in the playbook breaks. A fix from someone who works in that county is the most useful thing you can send.

## Never post real subject data

Not in an issue, a pull request, a commit or a screenshot: no subject address, PIN, MLS number, owner name, borrower, client or order number. That is confidential assignment information under USPAP. Use the test addresses in `README.md`, or describe the property in general terms ("a single-family lot in Wheaton").

Never attach a PNG or PDF from your `Workfiles` folder. CI rejects any PNG, PDF, log or state file.

## Report a broken site

Open an issue with:

* the county, and the deliverable (plat map, zoning, tax page, township card, MLS, flood, market graphs);
* the `step`, `where` and `seen` lines from `ErrorLog.txt` (remove the address first);
* what the page looks like now, in words.

## Send a fix

1. Fork the repo and make a branch.
2. Edit the county sheet (`playbook\counties\`), the deliverable spec (`playbook\deliverables\`) or the recipe (`playbook\recipes\`). Write the step as what a person does on the page ("search the PIN", "click Recorded Documents"), so any AI with any browser tool can follow it. Browser tool names belong only in `playbook\browser\`.
3. A new or moved township site goes in `playbook\townships.json` (the fetch adds it for you with `fetch.py township set`).
4. Run the checks:

   ```
   python fetch/fetch.py check
   python scripts/smoke_test.py
   python scripts/scrub_check.py
   ```

5. Open a pull request saying which county and what changed, and that you tested it on a test address.

## Writing style

Short and concrete. No em dashes. Plain words an appraiser uses.
