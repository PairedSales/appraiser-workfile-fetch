# Setup: Gemini (EXPERIMENTAL)

**Not tested.** Use this only if you are comfortable troubleshooting.

Gemini needs two things the other apps provide built in:

1. **A way to work in a folder and run commands**: Gemini CLI or Google Antigravity. Open it in the extracted folder, `Documents\appraiser-workfile-fetch-main`. It reads `GEMINI.md`, which points it to `START-HERE.md`.
2. **A way to control your own Chrome**, with your sign-ins: a Chrome-control add-on or extension for Gemini CLI or Antigravity. A separate browser with no sign-ins fails every MLS item.

Also:

* Install Python from python.org (tick **Add python.exe to PATH**).
* Make sure the Downloads folder is readable from where Gemini runs. If Chrome saves somewhere else, tell Gemini and it updates `local.json`.
* Turn on `setup\chrome\chrome-automation-on.reg` and sign in to connectMLS in Chrome.

Then say:

```
get the data for 123 Main St, Anytown, IL
```

The browser actions in the playbook are written for any tool, but there is no Gemini adapter yet in `playbook\browser\`. Gemini should read `claude-in-chrome.md` and `chatgpt.md` and map the same actions to its own tools. If you get it working, please send the adapter back as a pull request.
