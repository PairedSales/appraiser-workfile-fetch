#!/usr/bin/env python3
"""Exercise fetch.py end to end in --test mode, with no browser and no network.

    python scripts/smoke_test.py

Builds a throwaway copy of the folder in a temp directory, so nothing here touches the user's own
_data or Workfiles. Checks plan, county, signin, record (ok refused without a file, failed, na),
the 2-4 unit market graph rule, LOGIN_WALL never giving up, put, finish, ErrorLog.txt and index.
"""
import json, os, shutil, subprocess, sys, tempfile

SRC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def run(root, *args, ok=True):
    r = subprocess.run([sys.executable, os.path.join(root, "fetch", "fetch.py"), *args, "--test"],
                       cwd=root, capture_output=True, text=True)
    if ok and r.returncode != 0:
        sys.exit("FAILED: fetch.py %s\n%s%s" % (" ".join(args), r.stdout, r.stderr))
    return r


def main():
    tmp = tempfile.mkdtemp(prefix="awf-smoke-")
    root = os.path.join(tmp, "awf")
    try:
        shutil.copytree(SRC, root, ignore=shutil.ignore_patterns(".git", "_data", "Workfiles", "local.json", "__pycache__", "_local-notes"))
        addr = "100 W Main St, Anytown, IL 60000"
        p = json.loads(run(root, "plan", "--address", addr).stdout)
        slug = p["address"]["slug"]
        assert slug == "100-W-Main-St-Anytown-IL-60000", slug
        assert p["address"]["todo"] == {"county": ["lookup"]}, p["address"]["todo"]

        v = json.loads(run(root, "county", "--slug", slug, "--county", "DuPage", "--pin", "00-00-000-000", "--units", "2").stdout)
        assert "legal-description" in v["todo"]["county"], v["todo"]
        assert "township-card" in v["todo"]["township"], v["todo"]
        assert "mls-listing" in v["todo"]["mls"], v["todo"]

        p = json.loads(run(root, "plan", "--address", addr).stdout)
        assert p["signin_checks"] and p["signin_checks"][0]["site"] == "connectmls", p["signin_checks"]

        r = run(root, "record", "--slug", slug, "--item", "plat-map", "--status", "ok", ok=False)
        assert r.returncode != 0 and "REFUSED" in (r.stdout + r.stderr), "ok without a file must be refused"

        # signed out of connectMLS: MLS and market items become LOGIN_WALL, and never give up
        out = json.loads(run(root, "signin", "--slug", slug, "--site", "connectmls", "--status", "signed-out").stdout)
        assert set(out["recorded_login_wall"]) == {"mls-listing", "market-graphs", "market-conditions"}, out
        state = json.load(open(os.path.join(root, "_data", "_fetch-test", "_fetch-state.json"), encoding="utf-8"))
        assert state["addresses"][slug]["items"]["mls-listing"]["attempts"] == 0, "LOGIN_WALL must not count"

        # a normal failure counts
        run(root, "record", "--slug", slug, "--item", "zoning", "--status", "failed", "--reason", "SERVICE_DOWN",
            "--where", "example.gov", "--seen", "HTTP 503")
        r = run(root, "record", "--slug", slug, "--item", "zoning", "--status", "failed", "--reason", "NOPE", ok=False)
        assert r.returncode != 0, "unknown reason code must be refused"

        # 2-4 unit: six market graphs complete the item
        folder = os.path.join(root, "_data", "_fetch-test", "Workfiles", slug)
        scratch = os.path.join(root, "_data", "_fetch-test", "_scratch")
        os.makedirs(scratch, exist_ok=True)
        src = os.path.join(scratch, "x.png")
        open(src, "wb").write(b"\x89PNG test")
        for kind in ("median-sale-price", "average-sale-price", "median-market-time", "average-market-time",
                     "median-pct-orig-list-price", "average-pct-orig-list-price"):
            run(root, "put", "--src", src, "--dest", os.path.join(folder, "market-%s-%s.png" % (kind, slug)))
        run(root, "record", "--slug", slug, "--item", "market-graphs", "--status", "ok")
        r = run(root, "put", "--src", src, "--dest", os.path.join(folder, "market-median-sale-price-%s.png" % slug), ok=False)
        assert r.returncode != 0, "put must refuse to overwrite"

        run(root, "put", "--src", src, "--dest", os.path.join(folder, "plat-map-%s.png" % slug))
        run(root, "record", "--slug", slug, "--item", "plat-map", "--status", "ok")
        run(root, "record", "--slug", slug, "--item", "flood-map", "--status", "na", "--reason", "test")
        run(root, "note", "--slug", slug, "--text", "Flood point is on a panel boundary; check which panel applies")
        f = json.loads(run(root, "finish", "--slug", slug, "--zoning", "R-1 (Test)", "--summary", "test").stdout)
        assert f["errorlog"] and f["open_items"] >= 1, f
        log = open(os.path.join(folder, "ErrorLog.txt"), encoding="utf-8").read()
        assert "item: zoning" in log and "item: mls-listing" in log and "run the fetch for " + addr in log, log
        assert "item: market-graphs" not in log, "2-4 unit market graphs should be done"
        out = run(root, "index").stdout
        assert "open items:" in out, out
        assert run(root, "now").stdout.strip().isdigit()
        run(root, "check")
        print("smoke test: ok")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main()
