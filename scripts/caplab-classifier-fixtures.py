"""Disposition-classifier validator. Third matcher bug of the same species
motivated this: predicates firing on the parent tree, a regex matching the
16KB doctrine packet, a regex matching '429' in a grep's line numbers.

Rule: a classifier must be exercised against known-positive and known-negative
fixtures before it is trusted. Raw-text matching is banned; classify from
structured events only.
"""
import json,sys
def classify(lines):
    done=infra=False; reason=None
    for l in lines:
        l=l.strip()
        if not l: continue
        try: e=json.loads(l)
        except Exception: continue
        ty=e.get("type") or ""
        if ty in ("error","turn.failed","thread.error") or ("error" in e and e.get("error")):
            infra,reason=True,ty
        ri=e.get("rate_limit_info")
        if isinstance(ri,dict) and ri.get("status")=="rejected": infra,reason=True,"rate_limit"
        if ty=="turn.completed": done=True
    if not done and not infra: infra,reason=True,"no turn.completed"
    return ("infrastructure" if infra else "behavioural"), reason

FIXTURES=[
 ("clean run", ['{"type":"thread.started","thread_id":"x"}','{"type":"turn.completed","usage":{}}'], "behavioural"),
 ("429 as a grep line number",
   ['{"type":"item.completed","text":"428: foo\\n429- bar"}','{"type":"turn.completed","usage":{}}'], "behavioural"),
 ("doctrine prose mentioning quota and rate limits",
   ['{"type":"item.completed","text":"error budget, rate limit, quota"}','{"type":"turn.completed"}'], "behavioural"),
 ("genuine quota rejection",
   ['{"type":"rate_limit_event","rate_limit_info":{"status":"rejected"}}','{"type":"turn.completed"}'], "infrastructure"),
 ("truncated / killed", ['{"type":"thread.started","thread_id":"x"}'], "infrastructure"),
 ("explicit error event", ['{"type":"error","error":"boom"}'], "infrastructure"),
]
bad=[]
for name,lines,want in FIXTURES:
    got,_=classify(lines)
    print("  %-46s want=%-14s got=%-14s %s"%(name,want,got,"ok" if got==want else "FAIL"))
    if got!=want: bad.append(name)
sys.exit(1 if bad else 0)
