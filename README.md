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

1. Extract the folder
2. Create a new project in your AI desktop software (Claude, ChatGPT, Gemini), linking the extracted folder and your downloads folder.
3. Enable chrome computer use in ChatGPT. enable Enable full CDP access at the bottom. "Always Allow" downloads
4. Go to Chrome extension options for ChatGPT and 'Allow access to file URLs'

That's it, just say enter an address and it will pull all of the relevant data.

## License

MIT (`LICENSE`). Not affiliated with MRED, FEMA, any county or any township.
