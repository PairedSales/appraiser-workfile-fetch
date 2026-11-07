#!/usr/bin/env python3
"""Leak check for a public repo. Fails on any scrub-checklist term and on any captured file.

    python scripts/scrub_check.py            check the files git tracks (or would track)
    python scripts/scrub_check.py --all      check every file under the folder, ignored ones too

It looks for: personal paths, private terms (see private_terms), AMC and client names, Claude-only tool wording outside playbook/browser/, standing-permission
wording, direct server calls in the playbook, and any PNG, PDF, spreadsheet, log or state file. Real subject addresses, PINs and MLS
numbers cannot be listed here without publishing them, so it also flags any Illinois PIN-shaped
or MLS-shaped number outside the allow list below; check each hit by hand.

Exit code 0: clean. Exit code 1: hits (printed as path:line: term).
"""
import os, re, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SELF = os.path.relpath(os.path.abspath(__file__), ROOT).replace("\\", "/")

# term -> regex. Case-insensitive unless the pattern sets its own flags.
TERMS = {
    "Windows user path": r"C:\\\\?Users\\\\?(?!<you>)",
    "Coding Projects": r"Coding Projects",
    "old project name": r"Appraisal Order Automation",
    "cloud mount": r"\$HOME/mnt|/mnt/user-data|/mnt/",
    "old Reference folder": r"Reference\\\\",
    "old SearchResults folder": r"\bSearchResults\b(?!\.aspx)",
    "email address": r"[A-Za-z0-9._%+-]+@(?:gmail|yahoo|outlook|hotmail|icloud)\.com",
    "phone number": r"(?<![\d-])(?:\(\d{3}\)\s?|\d{3}[ .-])\d{3}[ .-]\d{4}(?![\d-])",
    "AMC or client": r"Class Valuation|\bReggora\b|ValueLink|Rocket Close|(?-i:Compass)\b",
    "orders sheet": r"orders\.xlsm",
    "standing permission": r"has set this task up|without stopping to ask \(",
    "Aivre": r"\bAivre\b",
}


def private_terms():
    """Names, machine names and the like that must never appear, kept out of the repo itself
    (listing them here would publish them). One regex per line, from scripts/scrub-terms.local
    (gitignored) and from the SCRUB_TERMS environment variable (a CI secret). Forks without the
    secret skip these and still run every public check."""
    rx = []
    p = os.path.join(ROOT, "scripts", "scrub-terms.local")
    if os.path.isfile(p):
        rx += [l.strip() for l in open(p, encoding="utf-8") if l.strip() and not l.startswith("#")]
    rx += [l.strip() for l in os.environ.get("SCRUB_TERMS", "").splitlines() if l.strip()]
    return {"private term %d" % i: r for i, r in enumerate(rx, 1)}
# Claude-only wording: allowed only in playbook/browser/ (and in this script and the setup page for Claude).
CLAUDE_ONLY = {
    "Claude tool name": r"mcp__",
    "ToolSearch": r"\bToolSearch\b",
    "cloud device tool": r"\bdevice_(bash|commit_files|stage_files)\b",
    "scheduled task wording": r"scheduled task",
    "model name": r"\b(Opus|Sonnet|Haiku|Fable)\b",
    "effort setting": r"\beffort\b",
    "Claude in Chrome tool": r"\b(save_to_disk|javascript_tool|get_page_text|tabs_context_mcp|browser_batch|resize_window)\b",
}
CLAUDE_ONLY_OK = ("playbook/browser/", "setup/claude-desktop.md", "guides/automating-it.md")
# "scheduled task" is a plain-English phrase in the guide and setup pages; tool names are not.
GUIDE_OK_TERMS = {"scheduled task wording"}

# The playbook browses like a person: no direct server calls (RULES.md, Browse like a person).
SERVER_CALLS = {
    "direct server call": r"\bfetch\s*\(|XMLHttpRequest|/rest/services|/sharing/rest|[?&]f=json|/query\?|/export\?|GeocodeServer|GPServer",
}
SERVER_CALLS_IN = ("playbook/",)

# Number shapes that might be a real subject. Cook-style PINs (14 digits as 2-2-3-3-4),
# collar county PINs (2-2-3-3), and 8-digit MLS numbers. Allowed: zero-filled or made-up examples.
NUMBER_SHAPES = {
    "PIN-shaped number": r"(?<![\d-])\d{2}-\d{2}-(?:\d{2}-)?\d{3}-\d{3}(?:-\d{4})?(?![\d-])",
    "MLS-shaped number": r"\bMLS\s*#?\s*(\d{8})\b",
}
NUMBER_OK = re.compile(r"^(?:\d{2}-00-(?:00-)?000-000(?:-0000)?|12345678|00000000)$")

BAD_EXT = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".pdf", ".xlsx", ".xlsm", ".xls", ".docx", ".zip",
           ".tgz", ".mp4", ".pyc", ".log", ".tsv"}
BAD_NAMES = {"errorlog.txt", "_fetch-state.json", "_run-log.txt", "_open-issues.tsv", "local.json", "_fetch.lock"}
BAD_DIRS = {"_to_delete", "__pycache__", "workfiles", "_data", "_scratch", "_fetch-test", "_local-notes"}
TEXT_EXT = {".md", ".py", ".json", ".txt", ".yml", ".yaml", ".reg", ".toml", ".cfg", ".ini", ".gitignore", ""}


def tracked_files(all_files):
    if not all_files:
        try:
            out = subprocess.run(["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
                                 cwd=ROOT, capture_output=True, check=True).stdout.decode("utf-8")
            return [f for f in out.split("\0") if f]
        except (OSError, subprocess.CalledProcessError):
            pass
    found = []
    for dp, dns, fns in os.walk(ROOT):
        dns[:] = [d for d in dns if d != ".git"]
        for f in fns:
            found.append(os.path.relpath(os.path.join(dp, f), ROOT).replace("\\", "/"))
    return found


def read_text(path):
    raw = open(path, "rb").read()
    if raw.startswith(b"\xff\xfe") or raw.startswith(b"\xfe\xff"):
        return raw.decode("utf-16", "replace")
    return raw.decode("utf-8", "replace")


def main():
    all_files = "--all" in sys.argv
    TERMS.update(private_terms())
    hits = []
    for rel in sorted(tracked_files(all_files)):
        rel = rel.replace("\\", "/")
        parts = [p.lower() for p in rel.split("/")]
        name = parts[-1]
        ext = os.path.splitext(name)[1].lower()
        if rel.startswith(".git/"):
            continue
        if any(p in BAD_DIRS for p in parts[:-1]):
            hits.append("%s: captured or local folder (%s)" % (rel, next(p for p in parts[:-1] if p in BAD_DIRS)))
            continue
        if ext in BAD_EXT or name in BAD_NAMES:
            hits.append("%s: captured, log or state file" % rel)
            continue
        if rel == SELF or ext not in TEXT_EXT and name not in (".gitignore", "license"):
            continue
        try:
            lines = read_text(os.path.join(ROOT, rel)).splitlines()
        except OSError as ex:
            hits.append("%s: unreadable (%s)" % (rel, ex))
            continue
        claude_ok = rel.startswith(CLAUDE_ONLY_OK)
        for n, line in enumerate(lines, 1):
            for label, rx in TERMS.items():
                if re.search(rx, line, re.I):
                    hits.append("%s:%d: %s" % (rel, n, label))
            for label, rx in CLAUDE_ONLY.items():
                if claude_ok and (rel.startswith("playbook/browser/") or rel == "setup/claude-desktop.md" or label in GUIDE_OK_TERMS):
                    continue
                flags = 0 if label == "model name" else re.I
                if re.search(rx, line, flags):
                    hits.append("%s:%d: %s" % (rel, n, label))
            if rel.startswith(SERVER_CALLS_IN):
                for label, rx in SERVER_CALLS.items():
                    if re.search(rx, line):
                        hits.append("%s:%d: %s" % (rel, n, label))
            for label, rx in NUMBER_SHAPES.items():
                for m in re.finditer(rx, line, re.I):
                    num = m.group(1) if m.groups() else m.group(0)
                    if not NUMBER_OK.match(num):
                        hits.append("%s:%d: %s %s (check: real subject?)" % (rel, n, label, num))
            if "\u2014" in line or "\u2013" in line:
                hits.append("%s:%d: em or en dash" % (rel, n))
    if hits:
        print("\n".join(hits))
        print("\n%d hit(s). Fix every one before pushing: git history is public." % len(hits))
        sys.exit(1)
    print("scrub check: clean")


if __name__ == "__main__":
    main()
