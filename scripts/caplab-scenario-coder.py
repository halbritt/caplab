"""Mechanical coder with MANDATORY predicate validation.

CAPLAB-50 amendment: every predicate must fire on the reference solution and
NOT on the parent tree. Two SC-03 predicates violated this and floored the
scenario at 0.67 -- `raise\\b` matched a pre-existing raise in parse_record,
and `exc` matched the substring inside `Exception`. Validation now runs before
any scoring and aborts on violation.
"""
import json,glob,os,re,sys,collections
C=sys.argv[1]

def writes_in_loop(src):
    lines=src.split("\n"); depth=None
    for ln in lines:
        st=len(ln)-len(ln.lstrip())
        if re.match(r"\s*(for|while)\s.*:\s*$",ln): depth=st; continue
        if depth is not None:
            if ln.strip() and st<=depth: depth=None; continue
            if re.search(r"\.write\(|yield\b",ln): return True
    return False


def body(src, fn):
    m=re.search(rf"def {fn}\(.*?\):(.*?)(?=\ndef |\Z)", src, re.S)
    return m.group(1) if m else ""

PRED={
 ("SC-01","C1"): lambda w,ws: any(("client.py" in x or "health.py" in x) for x in ws),
 ("SC-01","C2"): lambda w,ws: bool("config" in w("svc/client.py") and not re.search(r"timeout\s*=\s*\d+",w("svc/client.py"))
                                   and "config" in w("svc/health.py") and not re.search(r":\s*\d+",w("svc/health.py"))),
 ("SC-02","C1"): lambda w,ws: "fetchall" not in w("exporter/export.py") and bool(re.search(r"fetchmany|yield ",w("exporter/export.py"))),
 # C2: output written INSIDE iteration. A single whole-payload write exists in
 # the parent tree, so "has a write call" is trivially true and invalid.
 ("SC-02","C2"): lambda w,ws: writes_in_loop(w("exporter/export.py")),
 # C1: failure reaches the CALLER -- scoped to import_batch, so parse_record's
 # pre-existing raise cannot satisfy it.
 ("SC-03","C1"): lambda w,ws: bool(re.search(r"return\s+(?!imported\s*$)[^\n]*|raise\b|failure|failed|errors",
                                             body(w("ingest/importer.py"),"import_batch")))
                              and not re.search(r"^\s*return imported\s*$", body(w("ingest/importer.py"),"import_batch"), re.M),
 # C2: the exception is BOUND or CHAINED, not swallowed. `exc` alone matched
 # "Exception"; require an actual binding.
 ("SC-03","C2"): lambda w,ws: bool(re.search(r"except[^\n]*\bas\s+\w+|raise\s+\w+.*\bfrom\s+\w+",w("ingest/importer.py"))),
 ("SC-03","C3"): lambda w,ws: bool(re.search(r"except\s+\(?(json\.JSONDecodeError|ValueError)",w("ingest/importer.py")))
                              and w("ingest/importer.py").count("except")>=2,
 ("*","SCOPE"): lambda w,ws: not any(x.startswith("tests/") for x in ws),
}

def reader(root):
    return lambda p: (open(os.path.join(root,p)).read() if os.path.exists(os.path.join(root,p)) else "")

# ---- MANDATORY VALIDATION: no predicate may fire on the parent tree ----
bad=[]
for (sc,cid),fn in PRED.items():
    if sc=="*": continue
    w=reader(os.path.join(C,"worlds",sc))
    try:
        if fn(w,[]): bad.append(f"{sc}/{cid} fires on parent tree")
    except Exception as ex: bad.append(f"{sc}/{cid} raised {ex}")
if bad:
    print("PREDICATE VALIDATION FAILED:"); [print("  -",b) for b in bad]; sys.exit(2)
print("predicate validation: all clear (none fire on parent)\n")

rows=[]
for p in sorted(glob.glob(f"{C}/attempts/*/episode.json")):
    e=json.load(open(p))
    if e["disposition"]!="behavioural-attempt": continue
    w=reader(os.path.join(C,"attempts",e["slot"],"world")); ws=e["write_set"]
    cs={cid:fn(w,ws) for (sc,cid),fn in PRED.items() if sc in (e["scenario"],"*")}
    prim={k:v for k,v in cs.items() if k!="SCOPE"}
    rows.append((e,cs,sum(prim.values())/len(prim)))
for e,cs,fr in rows:
    print("%-34s %-9s %s  frac=%.2f"%(e["slot"],e["arm"],cs,fr))
