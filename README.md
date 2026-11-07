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

You need Windows, Google Chrome, an MRED connectMLS membership, and one of the AI apps below. About 20 minutes.

1. **Download.** On this page, click **Code**, then **Download ZIP**. Extract it into your Documents folder. You get `Documents\appraiser-workfile-fetch-main`.
2. **Set up your AI app.** Follow the page for your app. It covers the Chrome add-on, Python and the project:
   * Claude desktop app: `setup\claude-desktop.md`
   * ChatGPT desktop app or Codex: `setup\chatgpt.md`
   * Gemini (experimental): `setup\gemini-experimental.md`
3. **Turn on the Chrome setup.** In `setup\chrome\`, double-click `chrome-automation-on.reg` and approve the prompt. Read `setup\chrome\README.md` first: it changes how Chrome prints.
4. **Sign in to connectMLS** in that same Chrome.
5. **Run it.** In your AI project, type:

   ```
   run the fetch for 400 S Eagle St, Naperville, IL 60540
   ```

   Any wording works, such as "get the data for 400 S Eagle St". The first time, the AI checks your PC and installs what is missing. Your AI app or its Chrome add-on asks before it opens each new site. Allow them (`setup\allowed-sites.md` lists every one).

## Test addresses

Public buildings, one per county, so you can try it without using a client's property. They are tax exempt and rarely listed, so expect some tax, township and MLS items to come back "not applicable". That is normal.

| County | Address |
|---|---|
| Cook | Oak Park Village Hall, 123 Madison St, Oak Park, IL 60302 |
| DuPage | Naperville Municipal Center, 400 S Eagle St, Naperville, IL 60540 |
| Kane | Geneva City Hall, 22 S First St, Geneva, IL 60134 |
| Lake | Libertyville Village Hall, 118 W Cook Ave, Libertyville, IL 60048 |
| McHenry | Woodstock City Hall, 121 W Calhoun St, Woodstock, IL 60098 |
| Will | Joliet City Hall, 150 W Jefferson St, Joliet, IL 60432 |
| Kendall | Yorkville City Hall, 651 Prairie Pointe Dr, Yorkville, IL 60560 |
| DeKalb | DeKalb Municipal Building, 164 E Lincoln Hwy, DeKalb, IL 60115 |

## When something is missing

Open `Workfiles\<address>\ErrorLog.txt`. Each missing item says why and what you need to do first, if anything. Do that (usually: sign in to the site in Chrome), then say "run the fetch for <address>" again. It only fetches what is still missing.

## Updates

Download the newer ZIP and extract it over the same folder, replacing files. Your own files are safe: they live only in `Workfiles\`, `_data\` and `local.json`, which the ZIP does not contain.

## Want it to run on its own?

Just ask: "every night I want you to fetch the data for 123 Fake St." The AI sets it up. `guides\automating-it.md` has a few more examples.

## Contributing

County sites change. If a step breaks, please open an issue or a pull request (`CONTRIBUTING.md`). Never post a real subject address, PIN or MLS number: use the test addresses above.

## License

MIT (`LICENSE`). Not affiliated with MRED, FEMA, any county or any township.
