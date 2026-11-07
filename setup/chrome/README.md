# Chrome setup

Two files. Double-click one, approve the Windows prompt (it needs administrator rights), then in Chrome go to `chrome://policy` and click **Reload policies**.

* `chrome-automation-on.reg` turns the fetch settings on.
* `chrome-automation-off.reg` puts Chrome back to normal.

## What "on" changes

These are Chrome policies for your Windows account, written to the registry under `HKEY_LOCAL_MACHINE\SOFTWARE\Policies\Google\Chrome`. Open the file in Notepad to see every line.

* **Print saves a PDF.** Any Print button, Ctrl+P or a site's print link saves a PDF to Downloads with no print preview. The fetch needs this for tax pages, property cards and MLS reports.
  **Side effect: you cannot print on paper from Chrome while it is on.** Print paper from Edge or Acrobat, or run the off file first.
* **PDF links download** instead of opening in a Chrome tab, so the fetch can read them from disk.
* **No Save As prompt**, and sites may download several files in a row.
* **Downloads go to your Downloads folder.**

Chrome shows "Your browser is managed by your organization" while these are on. That is the policy, not a virus.

## If a printed PDF does not show up

Chrome sometimes saves silent prints to the last folder anyone picked in a Save as PDF window. To reset it: run the off file, press Ctrl+P on any page, choose Save as PDF and save it into Downloads once, then run the on file again.
