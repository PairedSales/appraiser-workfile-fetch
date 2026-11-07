# Setup: Claude desktop app

About 20 minutes, once.

## 1. Install Python

The fetch uses a small Python helper. If you are not sure whether you have Python, skip this: the AI checks on the first run and tells you.

1. Go to python.org, click **Downloads**, and download the latest Python 3 for Windows.
2. Run the installer. On the first screen, tick **Add python.exe to PATH**, then click **Install Now**.
3. Close and reopen the Claude app afterwards.

## 2. Install Claude in Chrome

1. In Chrome, install the **Claude in Chrome** extension from the Chrome Web Store and sign it in to your Claude account.
2. Go to `chrome://extensions`, click **Details** under Claude, and turn on **Allow access to file URLs**. The fetch needs this to find what Chrome downloads.

## 3. Create the project

1. Open the Claude desktop app and create a new project (for example "Workfile fetch").
2. Add the folder you extracted, `Documents\appraiser-workfile-fetch-main`.
3. Add your **Downloads** folder too. Chrome saves MLS PDFs and printed pages there, and the fetch picks them up from it.

## 4. Sign in

In the same Chrome, sign in to connectMLS. The fetch uses that session and never signs in for you. It also uses the same session for Infosparks.

## 5. First run

In the project, start a new chat and type:

```
run the fetch for 400 S Eagle St, Naperville, IL 60540
```

* The first time, Claude checks Python and the PDF tools. Let it install what is missing.
* Claude in Chrome asks before it opens each new site. Choose to always allow the sites in `allowed-sites.md`.
* Claude may ask before it runs a command or writes a file. You can allow those for this project.

Files land in `Workfiles\400-S-Eagle-St-Naperville-IL-60540\` inside the folder.

## If it goes wrong

* "Browser unavailable": Chrome must be open, with the Claude in Chrome extension signed in.
* Every MLS item says LOGIN_WALL: sign in to connectMLS in Chrome and run it again.
* DOWNLOAD_NOT_REACHABLE: the Downloads folder is not added to the project, or Chrome saves somewhere else. Add the folder, or tell Claude where Chrome saves and it updates `local.json`.
