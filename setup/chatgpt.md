# Setup: ChatGPT desktop app or Codex

1. **Connect your Chrome.** Connect ChatGPT's Browser Use to your own Chrome, the one where you are signed in to connectMLS. A browser ChatGPT opens on its own has none of your sign-ins.
2. **Turn on full CDP access.** In ChatGPT settings, under **Developer mode**, turn on **Enable full CDP access**. The fetch needs it: it captures every map and record as a full-resolution screenshot, and uses JavaScript to tidy the page before capturing. ChatGPT marks this "Elevated risk" because it can control all of Chrome; the playbook limits it to opening pages, clicking, typing, screenshots and page scripts, and never touches Chrome's settings, cookies or passwords.
3. **Make the project.** Create a project and give it the folder you extracted (`Documents\appraiser-workfile-fetch-main`) and your **Downloads** folder. In the project instructions, paste:

   ```
   Before any data fetch, read START-HERE.md in the linked folder and follow it.
   ```

4. **Sign in to connectMLS** in Chrome, then type:

   ```
   run the fetch for 400 S Eagle St, Naperville, IL 60540
   ```

ChatGPT may ask before it opens a site, takes a screenshot or runs a script. Allow them for this project (`allowed-sites.md` lists every site). If it says CDP access is off, turn it on (step 2) and run it again.
