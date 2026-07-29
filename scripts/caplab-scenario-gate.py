#!/usr/bin/env python3
"""Scenario acceptance gate for advisory-selection-001.

Mechanical checks only. Headroom is NOT checked here -- it is measured by
running the unaided arm, never asserted (CAPLAB-81's asserted-headroom
criterion failed on first contact with data).

Language-aware: an earlier version ran pytest against Go worlds and reported
"no tests", which was a gate defect, not a scenario defect.
"""
import json,os,re,glob,subprocess,sys

D = "docs/product/studies/advisory-selection-001/scenarios"
H = os.path.expanduser("~/.local/share/pincite/release")
DR, IX = H + "/doctrine", H + "/doctrine/runtime/doctrine-index.sqlite3"
ENV = {k: v for k, v in os.environ.items()
       if k not in ("PINCITE_TRACE_DIR", "PINCITE_TRACE_SESSION")}
ALWAYS = {"agent-conduct-authority-bounded-action", "universal-evidence-before-intervention",
          "universal-no-change-option", "universal-preserve-behavior-by-default",
          "universal-repository-contract-precedence", "universal-separate-semantic-structural-change"}
RESIDUE = re.compile(r"\.pytest_cache|__pycache__|\.venv|node_modules|\.egg-info|\.DS_Store")


def run_tests(world):
    if os.path.exists(os.path.join(world, "go.mod")):
        r = subprocess.run(["go", "test", "./..."], cwd=world, capture_output=True, text=True, timeout=300)
        return "passed" if r.returncode == 0 else "FAIL"
    r = subprocess.run([sys.executable, "-m", "pytest", "-q"], cwd=world,
                       capture_output=True, text=True, timeout=300)
    if r.returncode == 0: return "passed"
    return "no tests" if "no tests ran" in (r.stdout + r.stderr) else "FAIL"


def retrieval(cid, task):
    out = "/tmp/_gate_packet.json"
    subprocess.run([DR + "/bin/pincite", "--doctrine-root", DR, "--index", IX,
                    "--role", "coding-agent", "--task", "defect-repair",
                    "--question", re.sub(r"\s+", " ", task)[:1500],
                    "--render", "none", "--out", out], capture_output=True, env=ENV)
    try:
        return cid in json.load(open(out))["activated_concepts"]
    except Exception:
        return None


def main():
    fails, hit, elig = [], 0, 0
    print("%-52s %5s %-7s %-8s %-6s %s" % ("scenario", "words", "tests", "residue", "codes", "retrieval"))
    for d in sorted(glob.glob(f"{D}/[0-9][0-9]-*")):
        n = os.path.basename(d); cid = n.split("-", 1)[1]
        task = open(f"{d}/TASK.md").read()
        words = len(re.sub(r"^\s*(python3|go |#).*$", "", task, flags=re.M).split())
        wok = 60 <= words <= 140
        res = [p for p in glob.glob(f"{d}/world/**/*", recursive=True)
               if os.path.isfile(p) and RESIDUE.search(p)]
        tests = run_tests(f"{d}/world")
        try:
            cs = json.load(open(f"{d}/codes.json"))["codes"]
            cok = len(cs) >= 2 and any(c["id"] == "SCOPE" for c in cs) and all(c.get("negative_space") for c in cs)
        except Exception:
            cok = False
        if cid in ALWAYS:
            rank = "n/a always-load"
        else:
            elig += 1; h = retrieval(cid, task)
            rank = "HIT" if h else ("miss" if h is False else "ERR"); hit += bool(h)
        for ok, why in ((wok, "word count"), (tests == "passed", "tests"),
                        (not res, "residue"), (cok, "codes")):
            if not ok: fails.append(f"{n}: {why}")
        print("%-52s %5d %-7s %-8s %-6s %s" % (n, words, tests,
              "clean" if not res else f"{len(res)} files", "ok" if cok else "BAD", rank))
    print(f"\nPART 1 retrieval: {hit}/{elig} eligible scenarios serve their own concept")
    if fails:
        print("\nGATE FAILURES:"); [print("  -", f) for f in fails]; return 1
    print("gate: all mechanical checks pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
