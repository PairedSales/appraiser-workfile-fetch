# Appraiser Workfile Fetch

Give your AI app one address. It opens the county, township, FEMA and MLS sites in your own Chrome, the way you would, and saves the workfile documents into a folder for that property.

Built for residential appraisers in the Chicago area: Cook, DuPage, Kane, Lake, McHenry, Will, Kendall and DeKalb counties. It works with the Claude desktop app and with ChatGPT (desktop app or Codex). Gemini is experimental.

It is a set of written instructions plus a small Python helper. It is not a scraper and not a service: everything runs on your own PC, in your own browser, with your own sign-ins.

## What it saves

For every property, in `Workfiles\<address>\`:

* **Plat map** (county parcel map, lot dimensions readable)
* **Zoning map** with the subject ringed and the district named
* **FEMA flood map** (FIRMette) with zone, SFHA yes or no, panel, effective date and distance to the nearest flood hazard
* **Every MLS listing** of the subject, any status, any age (connectMLS PDF)
* **Eight Infosparks market graphs** for the city or Chicago neighborhood (six for 2 to 4 units, which have no price per sq ft) and a **market conditions PDF** built from them

By county:

| County | Also saves |
|---|---|
| Cook | Recorded legal description, tax page PDF |
| DuPage, Kane, DeKalb | Recorded legal description, township assessor record |
| Will | County property card PDF, township assessor record |
| McHenry | Tax page PDF, township assessor record |
| Kendall | Township assessor record |
| Lake | (no free legal images; the assessor's abbreviated legal is noted instead) |

The township assessor record is the township's card, its record card PDF, the sketch and the photo, when the township publishes them online. Many do; some publish nothing, and that is noted, not treated as an error.

Anything it could not get goes into `ErrorLog.txt` in the property folder, with the reason. The usual reason is "sign in to connectMLS in Chrome".

## What it never does

* Never signs in for you or types a password.
* Never buys, pays, subscribes or accepts terms.
* Never changes a record or sends anything. It only searches, views, prints and downloads.
* Never solves a CAPTCHA.
* Never sends your files anywhere. Everything stays in the folder on your PC.

You still verify every record. See `DISCLAIMER.md`.

## Install

You need Windows, Chrome, a connectMLS membership and an AI app.

1. Click **Code**, then **Download ZIP**, and extract it anywhere.
2. Set up your AI app: `setup\claude-desktop.md`, `setup\chatgpt.md` (ChatGPT or Codex), or `setup\gemini-experimental.md`.
3. Double-click `setup\chrome\chrome-automation-on.reg` and approve the prompt. It makes Chrome save prints as PDFs (`setup\chrome\README.md`).
4. Sign in to connectMLS in Chrome.

Then ask:

> Get the data for 123 Main St, Anytown, IL.

The first time, allow what it asks for.

## Using it

> What is still missing for 123 Main St?

> Every night I want you to fetch the data for 123 Main St.

Asking for an address again fetches only what is still missing. `guides\automating-it.md` has more examples.

## License

Public domain ([The Unlicense](LICENSE)). Use it, change it, sell it, no credit needed. Not affiliated with MRED, FEMA, any county or any township.
