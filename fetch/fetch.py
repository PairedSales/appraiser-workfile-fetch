#!/usr/bin/env python3
r"""Bookkeeping for the appraiser workfile fetch.

Run every command from the folder root (the folder that holds START-HERE.md):
    python fetch/fetch.py <command> ...

The browsing is done by the AI following the playbook files in playbook\. This script only
decides WHAT is needed and records WHAT happened, so the playbook never has to describe file
names, dedupe, ErrorLog.txt or the run log by hand.

Commands
  doctor   check Python, the PDF tools, the Downloads folder and the Workfiles folder.
           Writes local.json on the first run. Run it before the first fetch.
  plan     --address "<address>" [--unattended] [--test]
           Print the worklist for one address as JSON: which procedures and items are still
           missing and exactly which playbook files to read.
  signin   --slug S --site connectmls --status signed-in|signed-out [--test]
           Record the sign-in check made at the start of a run. signed-out records every item
           that needs that site as LOGIN_WALL without visiting it.
  county   --slug S --county KEY [--pin P] [--lon X --lat Y] [--muni M]
           [--abbrev-legal TEXT] [--units N] [--test]
           Record the county and PIN found by the county lookup. An unsupported county marks
           the address out of area. Prints the address's updated todo.
  record   --slug S --item KEY --status ok|failed|na [--reason CODE] [--step ..] [--where ..]
           [--seen ..] [--needs ..] [--files ..] [--note TEXT] [--units N] [--test]
           Record the result of one item. "ok" is refused unless the file(s) are really in the
           property folder.
  note     --slug S --text TEXT [--test]      add a NOTES line to the address
  finish   --slug S [--zoning TEXT] [--summary TEXT] [--test]
           Write ErrorLog.txt (only when needed) and append the run log line.
  index    [--test]   rebuild _data\_open-issues.tsv from every ErrorLog.txt
  status   --slug S [--test]   show state and files for one address
  now      print the time as epoch seconds (for grab-download --since)
  put      --src FILE --dest PATH [--replace]
           Copy a finished capture into a property folder (temp name, then rename).
  grab-download --since EPOCH (--match "w1,w2" | --name "w1" | --size BYTES) --dest PATH [--trim-blank]
           Find the newest download made after EPOCH that matches, and copy it to PATH.
  township lookup|set --county KEY ...    the township assessor registry (townships.json)
  check    validate config.json and that every playbook file it names exists
  setup    [--downloads PATH]   write local.json (doctor does this for you)

--test keeps everything (folders, state, logs) under _data\_fetch-test\.
"""
import argparse, datetime as dt, json, os, re, shutil, subprocess, sys, time, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))           # <root>\fetch
ROOT = os.path.dirname(HERE)                                # the linked folder
PLAYBOOK = os.path.join(ROOT, "playbook")
CFG = json.load(open(os.path.join(PLAYBOOK, "config.json"), encoding="utf-8"))
LOCAL_FILE = os.path.join(ROOT, "local.json")               # this PC's settings, never committed
LOCAL = {}
if os.path.exists(LOCAL_FILE):
    try:
        LOCAL = json.load(open(LOCAL_FILE, encoding="utf-8"))
    except ValueError as ex:
        sys.exit("local.json does not parse (%s): fix it or delete it and run fetch.py doctor" % ex)

ITEM_ORDER = list(CFG["deliverables"].keys())
LABELS = {"legal-description": "Legal", "plat-map": "Plat", "zoning": "Zoning", "tax-page": "Tax page",
          "property-card": "Property card", "mls-listing": "MLS", "flood-map": "Flood", "market-graphs": "Market",
          "market-conditions": "Market conditions PDF",
          "township-card": "Township card", "township-prc": "Township record card PDF",
          "township-sketch": "Township sketch", "township-photo": "Township photo"}


class ToolMissing(Exception):
    """A helper program or Python package the step needs is not installed."""


# ---------------------------------------------------------------- time
def now_local():
    tz = CFG.get("timezone", "America/Chicago")
    try:
        from zoneinfo import ZoneInfo
        return dt.datetime.now(ZoneInfo(tz))
    except Exception:
        return dt.datetime.now()


def today():
    return now_local().strftime("%Y-%m-%d")


def stamp():
    return now_local().strftime("%Y-%m-%d %H:%M")


def rel(p):
    """A path relative to the folder root, for output the AI and the user read."""
    try:
        r = os.path.relpath(p, ROOT)
        return p if r.startswith("..") else r
    except ValueError:
        return p


# ---------------------------------------------------------------- paths
def default_downloads():
    return os.path.join(os.path.expanduser("~"), "Downloads")


class Paths:
    def __init__(self, test=False):
        data = os.path.join(ROOT, CFG["data_dir"])
        base = os.path.join(data, CFG["test_root"]) if test else data
        self.test = test
        self.data = base
        self.workfiles = os.path.join(base, CFG["workfiles_dir"]) if test else os.path.join(ROOT, CFG["workfiles_dir"])
        self.state = os.path.join(base, CFG["state_file"])
        self.lock = os.path.join(base, CFG["lock_file"])
        self.run_log = os.path.join(base, CFG["run_log"])
        self.issues = os.path.join(base, CFG["issues_index"])
        self.scratch = os.path.join(base, "_scratch")
        self.to_delete = os.path.join(base, "_to_delete")
        self.downloads = [LOCAL.get("downloads_dir") or default_downloads()]

    def ensure(self):
        for d in (self.data, self.workfiles, self.scratch):
            os.makedirs(d, exist_ok=True)

    def folder(self, slug):
        return os.path.join(self.workfiles, slug)


def safe_write(path, text):
    """Write a whole file: temp name in the same folder, then rename over the target."""
    d = os.path.dirname(path)
    os.makedirs(d, exist_ok=True)
    tmp = os.path.join(d, ".tmp-" + os.path.basename(path))
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    try:
        os.replace(tmp, path)
    except OSError:
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(text)
        try:
            os.remove(tmp)
        except OSError:
            pass


# ---------------------------------------------------------------- state (with a lock)
class StateLock:
    """Only one fetch.py command changes the state file at a time. Each command holds the lock
    for well under a second; a lock older than stale_after is left over from a crash."""

    def __init__(self, P, wait=30, stale_after=120):
        self.P, self.wait, self.stale_after = P, wait, stale_after

    def __enter__(self):
        os.makedirs(os.path.dirname(self.P.lock), exist_ok=True)
        t0 = time.time()
        while True:
            try:
                fd = os.open(self.P.lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                with os.fdopen(fd, "w") as f:
                    f.write("pid %d at %s\n" % (os.getpid(), stamp()))
                return self
            except FileExistsError:
                try:
                    if time.time() - os.path.getmtime(self.P.lock) > self.stale_after:
                        os.remove(self.P.lock)
                        continue
                except OSError:
                    continue
                if time.time() - t0 > self.wait:
                    holder = ""
                    try:
                        holder = open(self.P.lock, encoding="utf-8").read().strip()
                    except OSError:
                        pass
                    sys.exit("state file is locked by another fetch.py (%s): wait and run it again" % holder)
                time.sleep(0.5)

    def __exit__(self, *exc):
        try:
            os.remove(self.P.lock)
        except OSError:
            pass


def load_state(P):
    if os.path.exists(P.state):
        with open(P.state, encoding="utf-8") as f:
            return json.load(f)
    return {"version": 2, "addresses": {}}


def save_state(P, S):
    safe_write(P.state, json.dumps(S, indent=1, ensure_ascii=False))


def entry(S, slug):
    return S["addresses"].setdefault(slug, {"items": {}, "notes": [], "history": [], "run": {}})


# ---------------------------------------------------------------- addresses
def slug_of(a):
    s = re.sub(r'[<>:"/\\|?*,#]', ' ', str(a))
    return re.sub(r'\s+', ' ', s).strip().replace(' ', '-')


ADDR_RE = re.compile(r'^\s*\d[\dA-Za-z-]*\s+\S')


def is_multi_unit(e):
    try:
        return int(e.get("units") or 1) >= 2
    except (TypeError, ValueError):
        return False


# ---------------------------------------------------------------- deliverables
def expected_files(key, slug, e=None):
    d = CFG["deliverables"][key]
    if "files" in d:
        out = [f.format(slug=slug) for f in d["files"]]
        if e is not None and is_multi_unit(e) and d.get("not_for_multi_unit"):
            skip = {f.format(slug=slug) for f in d["not_for_multi_unit"]}
            out = [f for f in out if f not in skip]
        return out
    if "any_of" in d:
        return [f.format(slug=slug) for f in d["any_of"]]
    return [d["prefix"] + d.get("suffix", "").format(slug=slug) + d["ext"]]


def present(key, slug, folder, e=None):
    """(is_complete, missing_file_names)"""
    d = CFG["deliverables"][key]
    have = set(os.listdir(folder)) if os.path.isdir(folder) else set()
    sub = os.path.join(folder, d.get("subfolder", ""))
    if d.get("subfolder") and os.path.isdir(sub):
        have |= set(os.listdir(sub))
    if "files" in d:
        miss = [f for f in expected_files(key, slug, e) if f not in have]
        return (not miss, miss)
    if "any_of" in d:
        ok = any(f in have for f in expected_files(key, slug))
        return (ok, [] if ok else [" or ".join(expected_files(key, slug))])
    # numbered copies: mls-listing-<year>-<MLS#>-<slug>.pdf, ...
    pre, tail = d["prefix"], (d.get("suffix", "").format(slug=slug) + d["ext"]).lower()
    ok = any(f.startswith(pre) and f.lower().endswith(tail) for f in have)
    return (ok, [] if ok else [pre + d.get("suffix", "").format(slug=slug) + d["ext"]])


def files_line(key, slug, missing=None):
    d = CFG["deliverables"][key]
    if missing and d.get("all_files"):
        return ", ".join(missing)
    if "hint" in d:
        return d["hint"].format(slug=slug)
    if "prefix" in d:
        p, s = d["prefix"], d.get("suffix", "").format(slug=slug) + d["ext"]
        return p + s + " (more than one: " + p + "-2" + s + ", " + p + "-3" + s + " ...)"
    return " or ".join(expected_files(key, slug))


def applicability(key, county):
    """None if the item applies to this address, else the reason it does not."""
    c = CFG["counties"].get(county)
    d = CFG["deliverables"][key]
    if county in d.get("skip_counties", []):
        return "no township assessor lookup in " + c["name"] + " County"
    if d["procedure"] == "county":
        if key in c["deliverables"]:
            return None
        if key == "legal-description":
            return c.get("no_legal", "no legal description in " + c["name"] + " County")
        if key == "tax-page":
            return "no tax page for " + c["name"] + " County"
        if key == "property-card":
            return "no property card capture for " + c["name"] + " County"
        return "not a " + c["name"] + " County deliverable"
    return None


def counts_toward_giving_up(st):
    return st.get("reason") not in CFG.get("reasons_that_never_give_up", [])


def item_status(key, slug, county, e, folder, unattended):
    """done | na | gave-up | missing"""
    ok, miss = present(key, slug, folder, e)
    if ok:
        return "done", None
    why = applicability(key, county)
    if why:
        return "na", why
    st = e["items"].get(key, {})
    if st.get("status") == "na":
        return "na", st.get("na_reason") or "not applicable"
    if unattended and st.get("status") == "failed" and st.get("attempts", 0) >= CFG["max_attempts"]:
        return "gave-up", None
    return "missing", None


def address_view(P, S, rec, unattended=False):
    slug = rec["slug"]
    e = entry(S, slug)
    if rec.get("address"):
        e["address"] = rec["address"]
    folder = P.folder(slug)
    v = {"address": e["address"], "slug": slug, "folder": rel(folder),
         "county": e.get("county"), "pin": e.get("pin"), "units": e.get("units"),
         "point": e.get("point"), "muni": e.get("muni"),
         "todo": {}, "done": [], "not_applicable": {}, "gave_up": [], "read": []}
    county = e.get("county")
    if e.get("out_of_area"):
        v["out_of_area"] = e["out_of_area"]
        return v
    if county not in CFG["counties"]:
        lk = e["items"].get("ALL", {})
        if unattended and lk.get("status") == "failed" and lk.get("attempts", 0) >= CFG["max_attempts"]:
            v["gave_up"].append("ALL")
            return v
        v["todo"]["county"] = ["lookup"]
        v["read"] = [CFG["lookup_spec"], "recipes/browser.md"]
        return v
    c = CFG["counties"][county]
    reads = []
    for key in ITEM_ORDER:
        st, why = item_status(key, slug, county, e, folder, unattended)
        d = CFG["deliverables"][key]
        if st == "done":
            v["done"].append(key)
        elif st == "na":
            v["not_applicable"][key] = why
        elif st == "gave-up":
            v["gave_up"].append(key)
        else:
            v["todo"].setdefault(d["procedure"], []).append(key)
    for proc in CFG["procedure_order"]:
        if proc not in v["todo"]:
            continue
        if proc == "county":
            reads += [c["sheet"]] + [CFG["deliverables"][k]["spec"] for k in v["todo"][proc]]
            reads += ["recipes/%s.md" % r for r in c["recipes"]]
        else:
            for k in v["todo"][proc]:
                reads.append(CFG["deliverables"][k]["spec"])
                reads += ["recipes/%s.md" % r for r in CFG["deliverables"][k].get("recipes", [])]
    seen = set()
    v["read"] = [r for r in reads if not (r in seen or seen.add(r))]
    v["todo"] = {p: v["todo"][p] for p in CFG["procedure_order"] if p in v["todo"]}
    return v


def signin_checks(v):
    """Sites to check once at the start of the run, with the items that need them."""
    out = []
    for site, info in CFG.get("signin_sites", {}).items():
        items = [k for p in v["todo"].values() for k in p if CFG["deliverables"].get(k, {}).get("needs_signin") == site]
        if items:
            out.append({"site": site, "name": info["name"], "how": info["how"], "items": items})
    return out


# ---------------------------------------------------------------- commands
def cmd_plan(a, P):
    ad = (a.address or "").strip()
    if not ADDR_RE.match(ad):
        sys.exit("give one street address with a house number: plan --address \"123 Main St, Naperville, IL 60540\"")
    P.ensure()
    slug = slug_of(ad)
    with StateLock(P):
        S = load_state(P)
        v = address_view(P, S, {"address": ad, "slug": slug}, a.unattended)
        save_state(P, S)
    reads = list(CFG["always_read"]) + [r for r in v["read"] if r not in CFG["always_read"]]
    out = {
        "now": stamp(), "test": P.test, "root": ROOT,
        "workfiles": rel(P.workfiles), "scratch": rel(P.scratch),
        "read_these_first": ["playbook/" + r for r in reads] + [browser_adapter_hint()],
        "tools": {os.path.splitext(os.path.basename(t))[0]: "fetch/" + t for t in CFG["tools"]},
        "signin_checks": signin_checks(v),
        "address": v,
        "complete": not v["todo"] and not v.get("out_of_area") and not v["gave_up"],
    }
    print(json.dumps(out, indent=1, ensure_ascii=False))


def browser_adapter_hint():
    return "playbook/browser/ (read the one file that matches your browser tool)"


def find_slug(S, slug):
    if slug not in S["addresses"]:
        sys.exit("unknown slug %r: run plan --address first" % slug)
    return S["addresses"][slug]


def add_history(e, item, what, reason):
    line = "%s %s %s %s" % (today(), item, what, reason)
    if line not in e["history"]:
        e["history"].append(line)


def set_units(e, units):
    if units is not None:
        e["units"] = units


def record_failed(e, item, reason, step="", where="", seen="", needs="nothing", files=None):
    st = e["items"].setdefault(item, {})
    counted = reason not in CFG.get("reasons_that_never_give_up", [])
    if counted and (st.get("last_tried") != today() or st.get("status") != "failed"):
        st["attempts"] = st.get("attempts", 0) + 1
    st.setdefault("attempts", 0)
    st.setdefault("first_failed", today())
    st.update({"status": "failed", "last_tried": today(), "reason": reason or "OTHER",
               "step": step or "", "where": where or "", "seen": seen or "", "needs": needs or "nothing"})
    if files:
        st["files"] = files
    st["tried"] = True
    add_history(e, item, "FAILED", st["reason"])
    return st


def cmd_signin(a, P):
    if a.site not in CFG.get("signin_sites", {}):
        sys.exit("unknown site %r; known: %s" % (a.site, ", ".join(CFG.get("signin_sites", {}))))
    info = CFG["signin_sites"][a.site]
    with StateLock(P):
        S = load_state(P)
        e = find_slug(S, a.slug)
        S.setdefault("signin", {})[a.site] = {"status": a.status, "at": stamp()}
        marked = []
        if a.status == "signed-out":
            v = address_view(P, S, {"slug": a.slug})
            for k in [k for p in v["todo"].values() for k in p]:
                if CFG["deliverables"][k].get("needs_signin") == a.site:
                    record_failed(e, k, "LOGIN_WALL", step="sign-in check at the start of the run",
                                  where=info["domain"], seen="signed out of %s" % info["name"],
                                  needs="sign in to %s in Chrome" % info["name"])
                    e["run"].setdefault("notes", {}).setdefault(k, None)
                    marked.append(k)
        save_state(P, S)
    print(json.dumps({"site": a.site, "status": a.status, "recorded_login_wall": marked,
                      "tell_the_user": ("sign in to %s in Chrome, then run the fetch again" % info["name"]) if marked else None}))


def cmd_county(a, P):
    with StateLock(P):
        S = load_state(P)
        e = find_slug(S, a.slug)
        key = a.county.strip().upper().replace(" COUNTY", "").replace(" ", "")
        if key not in CFG["counties"]:
            e["out_of_area"] = a.county.strip().upper().replace(" COUNTY", "")
            e["county"] = e["out_of_area"]
            e["run"]["outcome"] = "skipped"
        else:
            e.pop("out_of_area", None)
            e["county"] = key
            if a.pin:
                e["pin"] = a.pin
            if a.lon is not None and a.lat is not None:
                e["point"] = [a.lon, a.lat]
            if a.muni:
                e["muni"] = a.muni
            if a.abbrev_legal:
                e["abbrev_legal"] = a.abbrev_legal
            set_units(e, a.units)
            if e["items"].get("ALL", {}).get("status") == "failed":
                add_history(e, "ALL", "FIXED", "ok")
                e["items"]["ALL"]["status"] = "ok"
        e["run"]["county_work"] = True
        v = address_view(P, S, {"slug": a.slug})
        save_state(P, S)
    print(json.dumps(v, indent=1, ensure_ascii=False))


def cmd_record(a, P):
    with StateLock(P):
        S = load_state(P)
        e = find_slug(S, a.slug)
        item = a.item
        if item != "ALL" and item not in CFG["deliverables"]:
            sys.exit("unknown item %r; keys: %s" % (item, ", ".join(ITEM_ORDER)))
        set_units(e, a.units)
        if a.status == "ok":
            st = e["items"].setdefault(item, {})
            if item != "ALL":
                ok, miss = present(item, a.slug, P.folder(a.slug), e)
                if not ok:
                    sys.exit("REFUSED: %s is not done, missing in %s: %s" % (item, rel(P.folder(a.slug)), ", ".join(miss)))
            if st.get("status") == "failed":
                add_history(e, item, "FIXED", "ok")
            st.update({"status": "ok", "last_tried": today(), "tried": True})
        elif a.status == "na":
            st = e["items"].setdefault(item, {})
            st.update({"status": "na", "na_reason": a.reason or a.seen or "not applicable", "last_tried": today(), "tried": True})
        else:
            if a.reason and a.reason not in CFG["reason_codes"]:
                sys.exit("unknown reason %r; codes: %s" % (a.reason, ", ".join(CFG["reason_codes"])))
            record_failed(e, item, a.reason or "OTHER", a.step, a.where, a.seen, a.needs, a.files)
        if item == "ALL" or CFG["deliverables"][item]["procedure"] == "county":
            e["run"]["county_work"] = True
        if a.note:
            e["run"].setdefault("notes", {})[item] = a.note
        else:
            e["run"].setdefault("notes", {}).setdefault(item, None)
        save_state(P, S)
    print("recorded %s %s %s" % (a.slug, item, a.status))


def cmd_note(a, P):
    with StateLock(P):
        S = load_state(P)
        e = find_slug(S, a.slug)
        if a.text not in e["notes"]:
            e["notes"].append(a.text)
        save_state(P, S)
    print("noted")


def default_note(item, st):
    lab = LABELS.get(item, item)
    s = (st or {}).get("status")
    if item == "mls-listing":
        if s == "na":
            r = st.get("na_reason", "")
            return lab + " none" if ("no listing" in r.lower() or "no current listing" in r.lower()) else lab + ": " + r
        if s == "failed":
            return lab + ": " + ("login wall" if st.get("reason") == "LOGIN_WALL" else st.get("reason", "failed"))
        return lab + ": saved"
    if s == "failed":
        return "%s: %s" % (lab, st.get("reason", "failed"))
    if s == "na":
        return "%s: n/a (%s)" % (lab, st.get("na_reason", ""))
    return "%s: saved" % lab


def build_errorlog(P, S, slug, e, v):
    county = e.get("county") or "UNKNOWN"
    miss_blocks = []
    if e["items"].get("ALL", {}).get("status") == "failed":
        st = e["items"]["ALL"]
        miss_blocks.append(("ALL", st, "playbook/" + CFG["lookup_spec"] + " (county lookup), then the county sheet",
                            "every county file for this address"))
    elif county in CFG["counties"]:
        c = CFG["counties"][county]
        for key in ITEM_ORDER:
            if key in v["done"] or key in v["not_applicable"]:
                continue
            st = e["items"].get(key, {})
            if st.get("status") != "failed":
                continue
            d = CFG["deliverables"][key]
            spec = "playbook/" + d["spec"] + ((" with playbook/" + c["sheet"]) if d["procedure"] == "county" else "")
            ok, miss = present(key, slug, P.folder(slug), e)
            miss_blocks.append((key, st, spec, files_line(key, slug, miss)))
    notes = e.get("notes", [])
    if e.get("out_of_area") or (not miss_blocks and not notes and not e.get("errorlog_written")):
        return None
    n = len(miss_blocks)
    if n:
        status = "OPEN, %d item(s) missing (updated %s)" % (n, stamp())
    elif notes:
        status = "OK, 0 item(s) missing (notes only)"
    else:
        status = "RESOLVED (%s)" % today()
    L = ["FETCH ERROR LOG",
         "Address: " + e.get("address", ""),
         "Slug: " + slug,
         "Folder: " + rel(P.folder(slug)),
         "County: %s | PIN: %s | Units: %s" % (county, e.get("pin") or "none", e.get("units") or "unknown"),
         "Status: " + status, "",
         'HOW TO RETRY: Fix anything on a "needs" line below (for example, sign in to the site in Chrome). '
         'Then, in the same AI project, say "run the fetch for ' + e.get("address", "<address>") + '". '
         'It fetches only the MISSING items below into the Folder above, then rewrites this file.', ""]
    for i, (key, st, spec, files) in enumerate(miss_blocks, 1):
        needs = st.get("needs") or "nothing"
        if st.get("attempts", 0) >= CFG["max_attempts"] and needs == "nothing":
            needs = "nothing (unattended runs stopped retrying after %d attempts; retry by hand)" % CFG["max_attempts"]
        L += ["MISSING %d" % i,
              "  item: " + key,
              "  spec: " + spec,
              "  files: " + (st.get("files") or files),
              "  reason: " + st.get("reason", "OTHER"),
              "  step: " + (st.get("step") or ""),
              "  where: " + (st.get("where") or ""),
              "  seen: " + (st.get("seen") or ""),
              "  needs: " + needs,
              "  first-failed: " + st.get("first_failed", today()),
              "  last-tried: " + st.get("last_tried", today()),
              "  attempts: %d" % st.get("attempts", 0), ""]
    L.append("DONE: " + ", ".join(v["done"]))
    L.append("NOT APPLICABLE: " + ", ".join("%s (%s)" % (k, r) for k, r in v["not_applicable"].items()))
    L.append("")
    if notes:
        L.append("NOTES")
        L += notes
        L.append("")
    L.append("HISTORY")
    L += e.get("history", [])
    return "\n".join(L) + "\n"


def cmd_finish(a, P):
    with StateLock(P):
        S = load_state(P)
        e = find_slug(S, a.slug)
        v = address_view(P, S, {"slug": a.slug})
        # files that appeared since a failure (fixed by hand or in a retry) count as fixed
        for key in v["done"]:
            st = e["items"].get(key)
            if st and st.get("status") == "failed":
                add_history(e, key, "FIXED", "ok")
                st["status"] = "ok"
        v = address_view(P, S, {"slug": a.slug})
        county = e.get("county") or "UNKNOWN"
        run = e.get("run", {})
        notes = run.get("notes", {})
        parts = [today(), e.get("address", ""), county if not e.get("out_of_area") else "NONE"]
        if e.get("out_of_area"):
            names = [c["name"] for c in CFG["counties"].values()]
            parts.append("SKIPPED not in %s or %s (%s County)" % (", ".join(names[:-1]), names[-1], e["out_of_area"].title()))
        elif e["items"].get("ALL", {}).get("status") == "failed":
            st = e["items"]["ALL"]
            parts.append("FAILED %s: %s" % (st.get("reason", ""), st.get("seen", "")))
        else:
            parts.append("PIN " + (e.get("pin") or "none"))
            if a.zoning:
                parts.append("Zoning " + a.zoning)
            if a.summary:
                parts.append(a.summary)
            c = CFG["counties"].get(county, {})
            county_items = [k for k in notes if k in CFG["deliverables"] and CFG["deliverables"][k]["procedure"] == "county"]
            if county_items or run.get("county_work"):
                for key in county_items:
                    st = e["items"].get(key, {})
                    if st.get("status") == "failed":
                        parts.append(default_note(key, st))
                if c.get("abbrev_legal") and e.get("abbrev_legal"):
                    parts.append("abbrev legal: %s (assessor abbreviated legal, not a recorded legal description)"
                                 % e["abbrev_legal"])
            for key in ITEM_ORDER:
                if key in notes and CFG["deliverables"][key]["procedure"] != "county":
                    if key.startswith("township-") and key != "township-card" and not notes[key] \
                            and e["items"].get(key, {}).get("status") != "failed":
                        continue        # the township-card note speaks for the township step
                    parts.append(notes[key] or default_note(key, e["items"].get(key)))
        text = build_errorlog(P, S, a.slug, e, v)
        open_items = [b for b in (text or "").splitlines() if b.startswith("  item: ")]
        if text:
            safe_write(os.path.join(P.folder(a.slug), "ErrorLog.txt"), text)
            e["errorlog_written"] = True
        if open_items:
            parts.append("ErrorLog: %d open (%s)" % (len(open_items), ", ".join(x.split(": ", 1)[1] for x in open_items)))
        line = " | ".join(p for p in parts if p)
        os.makedirs(os.path.dirname(P.run_log), exist_ok=True)
        with open(P.run_log, "a", encoding="utf-8", newline="\n") as f:
            f.write(line + "\n")
        e["run"] = {}
        save_state(P, S)
    print(json.dumps({"run_log_line": line, "errorlog": bool(text), "open_items": len(open_items)}, ensure_ascii=False))


def parse_errorlog(path):
    with open(path, encoding="utf-8", errors="replace") as f:
        lines = f.read().splitlines()
    head, items, cur = {}, [], None
    for line in lines:
        m = re.match(r"^(Address|Slug|Folder|County|Status):\s*(.*)$", line)
        if m and m.group(1) not in head:
            head[m.group(1)] = m.group(2).strip()
            continue
        if re.match(r"^MISSING\s+\d+\s*$", line):
            cur = {}
            items.append(cur)
            continue
        if cur is not None:
            m = re.match(r"^\s+([A-Za-z-]+):\s*(.*)$", line)
            if m:
                cur[m.group(1).lower()] = m.group(2).strip()
            elif line.strip() == "" or not line.startswith(" "):
                cur = None
    return head, items


def cmd_index(a, P):
    cols = ["address", "county", "item", "reason", "where", "step", "seen", "needs",
            "first-failed", "last-tried", "attempts", "slug", "folder"]
    clean = lambda v: re.sub(r"[\t\r\n]+", " ", str(v or "")).strip()
    rows, addrs = [], set()
    names = sorted(os.listdir(P.workfiles)) if os.path.isdir(P.workfiles) else []
    for name in names:
        p = os.path.join(P.workfiles, name, "ErrorLog.txt")
        if not os.path.isfile(p):
            continue
        head, items = parse_errorlog(p)
        if not head.get("Status", "").upper().startswith("OPEN"):
            continue
        for it in items:
            r = dict(it)
            r["address"] = head.get("Address", name)
            r["county"] = head.get("County", "").split("|")[0].strip()
            r["slug"] = head.get("Slug", name)
            r["folder"] = head.get("Folder", "")
            rows.append(r)
            addrs.add(r["address"])
    rows.sort(key=lambda r: (clean(r.get("address")).lower(), clean(r.get("item"))))
    safe_write(P.issues, "\t".join(cols) + "\n" + "".join("\t".join(clean(r.get(c)) for c in cols) + "\n" for r in rows))
    print("open items: %d across %d address(es) -> %s" % (len(rows), len(addrs), rel(P.issues)))


def cmd_status(a, P):
    S = load_state(P)
    e = find_slug(S, a.slug)
    v = address_view(P, S, {"slug": a.slug})
    print(json.dumps({"state": e, "view": v}, indent=1, ensure_ascii=False))


def cmd_now(a, P):
    print(int(time.time()))


# ---------------------------------------------------------------- files
def pdf_text(path, pages=3):
    """Text of the first pages of a PDF: PyMuPDF if installed, else poppler's pdftotext.
    Raises ToolMissing when neither is there, so a missing tool never looks like a missing file."""
    try:
        try:
            import pymupdf as fitz
        except ImportError:
            import fitz
        with fitz.open(path) as d:
            return "\n".join(d[i].get_text() for i in range(min(pages, d.page_count)))
    except ImportError:
        pass
    exe = shutil.which("pdftotext")
    if not exe:
        raise ToolMissing("no PDF text reader: pip install pymupdf (or install poppler's pdftotext)")
    r = subprocess.run([exe, "-l", str(pages), path, "-"], capture_output=True, text=True, timeout=60)
    if r.returncode != 0:
        raise ToolMissing("pdftotext failed on %s: %s" % (os.path.basename(path), r.stderr.strip()[:200]))
    return r.stdout


def doc_text(path):
    low = path.lower()
    if low.endswith(".pdf"):
        return pdf_text(path, 3)
    if low.endswith(".docx"):
        with zipfile.ZipFile(path) as z:
            return re.sub(r"<[^>]+>", " ", z.read("word/document.xml").decode("utf-8", "replace"))
    return ""


def trim_blank_print_pages(path):
    """Drop trailing pages of a Chrome print-to-PDF that carry only Chrome's own header and footer
    (date, page title, URL, page counter). A page with any other text, or with no text at all
    (a scan), is kept. Returns the number of pages dropped."""
    try:
        from pypdf import PdfReader, PdfWriter
    except ImportError:
        raise ToolMissing("--trim-blank needs pypdf: pip install pypdf")
    r = PdfReader(path)
    n = len(r.pages)
    if n < 2:
        return 0
    def norm(pg):   # page lines with Chrome's "n/m" page counter taken off the end
        out = [re.sub(r"\s*\b\d+/\d+$", "", l.strip()) for l in (pg.extract_text() or "").splitlines()]
        return [l for l in out if l]
    lines = [norm(pg) for pg in r.pages]
    first = set(lines[0])
    keep = n
    while keep > 1:
        ls = lines[keep - 1]
        if not ls or any(l not in first for l in ls):
            break
        keep -= 1
    if keep == n:
        return 0
    w = PdfWriter()
    for i in range(keep):
        w.add_page(r.pages[i])
    import io
    buf = io.BytesIO()
    w.write(buf)
    with open(path, "wb") as out:
        out.write(buf.getvalue())
    return n - keep


def copy_bytes(src, dest):
    """Stream the bytes into a temp name next to dest, then rename: a plain new file, never a link."""
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    tmp = os.path.join(os.path.dirname(dest), ".tmp-" + os.path.basename(dest))
    with open(src, "rb") as fi, open(tmp, "wb") as fo:
        shutil.copyfileobj(fi, fo, 1 << 20)
    os.replace(tmp, dest)


def inside(path, folder):
    path, folder = os.path.abspath(path).lower(), os.path.abspath(folder).lower()
    return path.startswith(folder.rstrip("\\/") + os.sep)


def cmd_put(a, P):
    src, dest = os.path.abspath(a.src), os.path.abspath(a.dest)
    if not os.path.isfile(src):
        sys.exit("no such file: " + src)
    if not inside(dest, P.workfiles):
        sys.exit("dest must be inside " + rel(P.workfiles))
    if os.path.exists(dest) and not a.replace:
        sys.exit("already there (a present file is done; pass --replace only to fix this run's own file): " + rel(dest))
    copy_bytes(src, dest)
    print(json.dumps({"saved": rel(dest), "bytes": os.path.getsize(dest)}))


def cmd_grab(a, P):
    words = [w.strip().lower() for w in (a.match or "").split(",") if w.strip()]
    names = [w.strip().lower() for w in (a.name or "").split(",") if w.strip()]
    if not words and not a.size and not names:
        sys.exit("give --match words (text documents), --name words (file name) or --size bytes (scans, images)")
    dest_abs = os.path.abspath(a.dest)
    if not inside(dest_abs, P.workfiles) and not inside(dest_abs, P.scratch):
        sys.exit("dest must be inside %s or %s" % (rel(P.workfiles), rel(P.scratch)))
    cands = []
    for d in P.downloads:
        if os.path.isdir(d):
            for f in os.listdir(d):
                p = os.path.join(d, f)
                if os.path.isfile(p) and os.path.getmtime(p) >= a.since - 5 and not f.endswith((".crdownload", ".tmp")):
                    cands.append((os.path.getmtime(p), p))
    # A silent print does not always land in Downloads: Chrome saves it to whatever folder was
    # last picked in a Save as PDF window. If that was somewhere inside this folder, find it there
    # too. Workfiles and _data are never searched, so a file saved by hand is never touched.
    skip = {CFG["workfiles_dir"].lower(), CFG["data_dir"].lower(), ".git", "playbook", "fetch"}
    for dp, dns, fns in os.walk(ROOT):
        if os.path.abspath(dp) == ROOT:
            dns[:] = [x for x in dns if x.lower() not in skip and not x.startswith(".")]
        else:
            dns[:] = [x for x in dns if not x.startswith(".")]
        for f in fns:
            if not f.lower().endswith(".pdf"):
                continue
            p = os.path.join(dp, f)
            try:
                mt = os.path.getmtime(p)
            except OSError:
                continue
            if mt >= a.since - 5 and os.path.abspath(p) != dest_abs:
                cands.append((mt, p))
    cands.sort(reverse=True)
    looked = []
    try:
        for _, p in cands:
            looked.append(os.path.basename(p))
            if a.size and os.path.getsize(p) != a.size:
                continue
            if names and not all(w in os.path.basename(p).lower() for w in names):
                continue
            t = re.sub(r"\s+", " ", doc_text(p)).lower() if words else ""
            if all(w in t for w in words):
                copy_bytes(p, dest_abs)
                trimmed = trim_blank_print_pages(dest_abs) if a.trim_blank and dest_abs.lower().endswith(".pdf") else 0
                moved = None
                if not any(inside(p, d) for d in P.downloads):
                    os.makedirs(P.to_delete, exist_ok=True)
                    moved = os.path.join(P.to_delete, "%d-%s" % (int(time.time()), os.path.basename(p)))
                    try:
                        os.rename(p, moved)
                        moved = rel(moved)
                    except OSError as ex:
                        moved = "could not move stray: %s" % ex
                print(json.dumps({"saved": rel(dest_abs), "from": p, "bytes": os.path.getsize(dest_abs),
                                  "blank_pages_dropped": trimmed, "stray_moved_to": moved}))
                return
    except ToolMissing as ex:
        print(json.dumps({"saved": None, "reason": "TOOL_MISSING", "detail": str(ex),
                          "fix": "run python fetch/fetch.py doctor"}))
        sys.exit(4)
    reach = [d for d in P.downloads if os.path.isdir(d)]
    print(json.dumps({"saved": None, "reason": "DOWNLOAD_NOT_REACHABLE" if not reach else "NOT_FOUND",
                      "download_folders_reachable": reach, "new_files_seen": looked}))
    sys.exit(3)


# ---------------------------------------------------------------- setup and doctor
def write_local(downloads=None):
    cur = dict(LOCAL)
    cur["downloads_dir"] = downloads or cur.get("downloads_dir") or default_downloads()
    cur["python"] = sys.executable
    safe_write(LOCAL_FILE, json.dumps(cur, indent=1) + "\n")
    LOCAL.clear()
    LOCAL.update(cur)
    return cur


def cmd_setup(a, P):
    cur = write_local(a.downloads)
    print(json.dumps({"wrote": rel(LOCAL_FILE), "settings": cur}, indent=1))


def cmd_doctor(a, P):
    rows = []

    def row(name, ok, detail, fix=""):
        rows.append({"check": name, "ok": bool(ok), "detail": detail, "fix": "" if ok else fix})

    if not os.path.exists(LOCAL_FILE) or a.downloads:
        write_local(a.downloads)
        rows.append({"check": "local.json", "ok": True, "detail": "written: " + json.dumps(LOCAL), "fix": ""})
    else:
        row("local.json", True, json.dumps(LOCAL))
    v = sys.version_info
    row("Python 3.9 or newer", v >= (3, 9), "%d.%d.%d at %s" % (v[0], v[1], v[2], sys.executable),
        "install Python 3.12 from python.org (tick 'Add python.exe to PATH')")
    for mod, pipname, why in (("pypdf", "pypdf", "drops Chrome's blank trailing print pages"),
                              ("PIL", "pillow", "stitches map tiles and composes exhibits"),
                              ("reportlab", "reportlab", "builds the market conditions PDF")):
        try:
            __import__(mod)
            row(pipname, True, why)
        except ImportError:
            row(pipname, False, why, "python -m pip install -r requirements.txt")
    try:
        try:
            import pymupdf  # noqa: F401
        except ImportError:
            import fitz  # noqa: F401
        row("PDF text reader", True, "PyMuPDF")
    except ImportError:
        exe = shutil.which("pdftotext")
        row("PDF text reader", bool(exe), ("pdftotext at " + exe) if exe else "neither PyMuPDF nor pdftotext found",
            "python -m pip install -r requirements.txt (installs PyMuPDF)")
    dl = P.downloads[0]
    ok = os.path.isdir(dl)
    row("Downloads folder", ok, dl,
        "set downloads_dir in local.json to Chrome's download folder, or run doctor --downloads \"<path>\"")
    if ok:
        try:
            n = len(os.listdir(dl))
            row("Downloads readable", True, "%d entries" % n)
        except OSError as ex:
            row("Downloads readable", False, str(ex), "link your Downloads folder to the AI project")
    try:
        P.ensure()
        probe = os.path.join(P.workfiles, ".doctor-probe")
        with open(probe, "w") as f:
            f.write("ok")
        os.remove(probe)
        row("Workfiles writable", True, rel(P.workfiles))
    except OSError as ex:
        row("Workfiles writable", False, str(ex), "extract the zip into Documents, not into a read-only or synced folder")
    bad = check_playbook()
    row("playbook complete", not bad, "ok" if not bad else "; ".join(bad), "download a fresh copy of the zip")
    failed = [r for r in rows if not r["ok"]]
    print(json.dumps({"ok": not failed, "checks": rows,
                      "next": "fix each failed check, then run doctor again" if failed else "ready: run the fetch"}, indent=1))
    sys.exit(1 if failed else 0)


def check_playbook():
    bad = []
    names = set()
    for k, c in CFG["counties"].items():
        names.add(c["sheet"])
        names.update("recipes/%s.md" % r for r in c["recipes"])
        for d in c["deliverables"]:
            if d not in CFG["deliverables"]:
                bad.append("%s names unknown deliverable %s" % (k, d))
    for k, d in CFG["deliverables"].items():
        names.add(d["spec"])
        names.update("recipes/%s.md" % r for r in d.get("recipes", []))
        if d["procedure"] not in CFG["procedure_order"]:
            bad.append("%s has unknown procedure %s" % (k, d["procedure"]))
        if d.get("needs_signin") and d["needs_signin"] not in CFG.get("signin_sites", {}):
            bad.append("%s needs unknown sign-in site %s" % (k, d["needs_signin"]))
    names.update(CFG["always_read"])
    names.add(CFG["lookup_spec"])
    names.add(CFG["townships_file"])
    names.update(CFG.get("browser_adapters", []))
    try:
        json.load(open(os.path.join(PLAYBOOK, CFG["townships_file"]), encoding="utf-8"))
    except Exception as ex:
        bad.append("%s does not parse: %s" % (CFG["townships_file"], ex))
    for n in sorted(names):
        if not os.path.isfile(os.path.join(PLAYBOOK, n)):
            bad.append("missing file playbook/" + n)
    for t in CFG["tools"]:
        if not os.path.isfile(os.path.join(HERE, t)):
            bad.append("missing file fetch/" + t)
    return bad


def cmd_check(a, P):
    bad = check_playbook()
    print("ok" if not bad else "\n".join(bad))
    sys.exit(1 if bad else 0)


# ---------------------------------------------------------------- township assessor registry
def _twp_path():
    return os.path.join(PLAYBOOK, CFG["townships_file"])


def _twp_load():
    return json.load(open(_twp_path(), encoding="utf-8"))


def _twp_find(reg, county, name):
    tw = reg.get(county, {}).get("townships", {})
    norm = lambda s: (s or "").lower().replace(".", "").replace("saint", "st")
    for k in tw:
        if norm(k) == norm(name):
            return k
    return None


def cmd_township(a, P):
    """lookup: which township a PIN is in and what the registry knows about its assessor site.
    set: record what was found (a site that works, or that the township publishes nothing online)."""
    reg = _twp_load()
    county = a.county.upper()
    if county not in CFG["counties"]:
        sys.exit("unknown county " + county)
    creg = reg.setdefault(county, {"prefixes": {}, "townships": {}})
    if a.action == "lookup":
        name = a.township
        how = "given"
        if not name and a.pin:
            pre = re.sub(r"\D", "", a.pin)[:2]
            name = creg.get("prefixes", {}).get(pre)
            how = "PIN prefix " + pre if name else None
            if isinstance(name, list):
                print(json.dumps({"county": county, "township": None, "candidates": name,
                                  "next": "PIN prefix %s covers %s: read the township from the county record or the township assessor's own search, then lookup --township" % (pre, " and ".join(name))}, ensure_ascii=False))
                return
        out = {"county": county, "township": name, "from": how}
        if not name:
            out["next"] = "township not known from the PIN: read it from the county record or the township assessor's own search (deliverables/township-card.md), then run lookup again with --township"
        else:
            k = _twp_find(reg, county, name) or name
            ent = creg.get("townships", {}).get(k)
            out["township"] = k
            out["entry"] = ent
            if not ent:
                out["next"] = "not in the registry: search for the township assessor site (deliverables/township-card.md, Finding a site), then township set"
            elif ent.get("status") == "none":
                age = None
                try:
                    age = (dt.date.fromisoformat(today()) - dt.date.fromisoformat(ent.get("checked", "2000-01-01"))).days
                except Exception:
                    pass
                if age is not None and age > reg.get("recheck_none_after_days", 180):
                    out["next"] = "registry says no online data, but that was checked %d days ago: search again, then township set" % age
                else:
                    out["next"] = "no online data: record the township items na"
            else:
                out["next"] = "use the site per its entry and deliverables/township-card.md"
        if a.slug and name:
            with StateLock(P):
                S = load_state(P)
                e = find_slug(S, a.slug)
                e["township"] = out["township"]
                save_state(P, S)
        print(json.dumps(out, ensure_ascii=False, indent=1))
        return
    # set
    if not a.township or a.status not in ("online", "none"):
        sys.exit("set needs --township and --status online|none")
    k = _twp_find(reg, county, a.township) or a.township
    ent = creg.setdefault("townships", {}).setdefault(k, {})
    ent.update({"status": a.status, "checked": today(), "source": a.source or "fetch run"})
    if a.status == "online":
        ent["tested"] = True
    for f in ("url", "platform", "how", "note"):
        val = getattr(a, f)
        if val is not None:
            ent[f] = val
    if a.prefix:
        creg.setdefault("prefixes", {})[a.prefix] = k
    tmp = _twp_path() + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        json.dump(reg, f, ensure_ascii=False, indent=1)
    os.replace(tmp, _twp_path())
    print(json.dumps({"saved": county + "/" + k, "entry": ent}, ensure_ascii=False))


def main():
    ap = argparse.ArgumentParser(description="Bookkeeping for the appraiser workfile fetch. Run from the folder root.")
    sub = ap.add_subparsers(dest="cmd", required=True)

    def add(name, f):
        p = sub.add_parser(name)
        p.add_argument("--test", action="store_true")
        p.set_defaults(fn=f)
        return p

    p = add("doctor", cmd_doctor)
    p.add_argument("--downloads", help="Chrome's download folder, if it is not <home>\\Downloads")
    p = add("setup", cmd_setup)
    p.add_argument("--downloads")
    p = add("plan", cmd_plan)
    p.add_argument("--address", required=True)
    p.add_argument("--unattended", action="store_true",
                   help="for a scheduled run: skip items that failed %d times" % CFG["max_attempts"])
    p = add("signin", cmd_signin)
    p.add_argument("--slug", required=True)
    p.add_argument("--site", required=True)
    p.add_argument("--status", required=True, choices=["signed-in", "signed-out"])
    p = add("county", cmd_county)
    p.add_argument("--slug", required=True)
    p.add_argument("--county", required=True)
    p.add_argument("--pin")
    p.add_argument("--lon", type=float)
    p.add_argument("--lat", type=float)
    p.add_argument("--muni")
    p.add_argument("--abbrev-legal")
    p.add_argument("--units", type=int, help="number of living units (2 to 4 for a 2-4 unit building)")
    p = add("record", cmd_record)
    p.add_argument("--slug", required=True)
    p.add_argument("--item", required=True)
    p.add_argument("--status", required=True, choices=["ok", "failed", "na"])
    for k in ("reason", "step", "where", "seen", "needs", "files", "note"):
        p.add_argument("--" + k)
    p.add_argument("--units", type=int)
    p = add("note", cmd_note)
    p.add_argument("--slug", required=True)
    p.add_argument("--text", required=True)
    p = add("finish", cmd_finish)
    p.add_argument("--slug", required=True)
    p.add_argument("--zoning")
    p.add_argument("--summary")
    add("index", cmd_index)
    p = add("status", cmd_status)
    p.add_argument("--slug", required=True)
    add("now", cmd_now)
    p = add("put", cmd_put)
    p.add_argument("--src", required=True)
    p.add_argument("--dest", required=True)
    p.add_argument("--replace", action="store_true")
    p = add("grab-download", cmd_grab)
    p.add_argument("--since", type=float, required=True)
    p.add_argument("--match", help="comma-separated words that must all be in the document text")
    p.add_argument("--name", help="comma-separated words that must all be in the file name")
    p.add_argument("--size", type=int)
    p.add_argument("--dest", required=True)
    p.add_argument("--trim-blank", action="store_true",
                   help="for a printed page: drop trailing pages that hold only Chrome's header/footer")
    add("check", cmd_check)
    p = add("township", cmd_township)
    p.add_argument("action", choices=["lookup", "set"])
    p.add_argument("--county", required=True)
    p.add_argument("--pin")
    p.add_argument("--township")
    p.add_argument("--slug")
    p.add_argument("--status")
    for k in ("url", "platform", "how", "note", "prefix", "source"):
        p.add_argument("--" + k)
    a = ap.parse_args()
    a.fn(a, Paths(a.test))


if __name__ == "__main__":
    main()
