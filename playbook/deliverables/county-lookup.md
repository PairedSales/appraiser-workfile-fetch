# County lookup: which county, and the PIN

Runs when the plan shows `"county": ["lookup"]`. The answer is stored by fetch.py, so an address is looked up once.

## 1. Which county

Most Chicago-area towns and ZIP codes lie in one county, and the town and ZIP in the address usually settle it. Some towns straddle county lines (Bartlett, Elgin, Aurora, Naperville, Barrington Hills, Bolingbrook, among others): for those, and for any town or ZIP you are not sure of, search the web for `<town> IL <ZIP> county`, and in a straddling town go straight to the county parcel viewers in step 2 (start with the county that holds most of the town). The county is a hint until a county's own parcel lookup finds the address.

## 2. Confirm with the county's own parcel lookup

Open the county sheet named by `config.json` for that county (`counties/<county>.md`) and run its **Parcel lookup** section: search the address in the county's own parcel viewer or record search, the way the page expects it. It returns the PIN and the municipality, and it is the proof. Then:

```bash
python fetch/fetch.py county --slug <slug> --county <KEY> --pin <pin> --muni "<municipality or UNINCORPORATED>" [--abbrev-legal "<assessor abbreviated legal>"]
```

KEY is the config key: COOK, DUPAGE, KANE, LAKE, MCHENRY, WILL, KENDALL, DEKALB. Give `--abbrev-legal` for counties with no recorded legal (Lake, McHenry, Will, Kendall), verbatim from the assessor, when the sheet shows where to read it. fetch.py prints the address's real todo and the files to read next.

## 3. When the hinted county has no parcel

Try the neighbouring supported counties' parcel lookups, with the relaxed matching each sheet describes, before giving up.

* Found in one of them: record it as above. Add a note if the town or ZIP pointed elsewhere.
* The town and ZIP are clearly in a county this system does not cover (for example Grundy), and no covered county has the address: `fetch.py county --slug <slug> --county "<That County>"`. It is then skipped until that county is added.
* A covered county, but its parcel lookup cannot find the address (recorder typos happen: a street name can be indexed misspelled): do not call it out of area. Try the county's alternative lookups in its sheet, then `fetch.py record --slug <slug> --item ALL --status failed --reason NOT_FOUND --step "<which lookups>" --where "<sites>" --seen "<what came back>"`.
* Nothing anywhere: the same failed ALL record. It comes back on the next nights, then waits for a retry by hand.

Never capture a neighbouring parcel because it was the nearest thing found. An uncertain match (same house number on a similar street in another town) is `--reason UNCERTAIN_MATCH`, never a guess.
